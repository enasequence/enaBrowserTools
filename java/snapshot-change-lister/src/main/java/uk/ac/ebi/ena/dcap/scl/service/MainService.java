/*******************************************************************************
 * Copyright 2021 EMBL-EBI, Hinxton outstation
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 ******************************************************************************/
package uk.ac.ebi.ena.dcap.scl.service;

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.collections4.ListUtils;
import org.apache.commons.io.IOUtils;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import uk.ac.ebi.ena.dcap.scl.model.DataType;
import uk.ac.ebi.ena.dcap.scl.model.DiffFiles;
import uk.ac.ebi.ena.dcap.scl.model.Line;

import java.io.*;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.List;
import java.util.concurrent.*;

import static uk.ac.ebi.ena.dcap.scl.model.Line.POISON;

@Service
@Slf4j
public class MainService {

    private static final String BROWSER_API_EMBL = "https://www.ebi.ac.uk/ena/browser/api/%s/";
    final ExecutorService executorService = Executors.newFixedThreadPool(2);

    @Autowired
    PortalApiClient portalApiClient;


    public File writeLatestSnapshot(DataType dataType, File outputLocation, String fileName, String query) {

        File outFile = new File(outputLocation.getAbsolutePath() + File.separator + fileName + ".tsv");
        if (outFile.exists()) {
            outFile.delete();
        }
        return portalApiClient.getLatestSnapshot(dataType, outFile, query);
    }

    @SneakyThrows
    public DiffFiles compareSnapshots(File previousSnapshot, File latestSnapshot, File outputLocation, String namePrefix) {
        log.info("comparing:{} and {}", previousSnapshot.getAbsolutePath(), latestSnapshot.getAbsolutePath());
        File newOrUpdated = new File(outputLocation.getAbsolutePath() + File.separator + namePrefix + "_new-or" +
                "-updated.tsv");
        if (newOrUpdated.exists()) {
            newOrUpdated.delete();
        }
        File deleted = new File(outputLocation.getAbsolutePath() + File.separator + namePrefix + "_deleted.tsv");
        if (deleted.exists()) {
            deleted.delete();
        }

        BlockingQueue<Line> prevQ = new LinkedBlockingQueue<>(1000);
        BlockingQueue<Line> nextQ = new LinkedBlockingQueue<>(1000);

        final Future<?> prevFuture = executorService.submit(new Runnable() {
            @Override
            public void run() {
                loadToQueues(previousSnapshot, prevQ);
            }
        });
        final Future<?> newFuture = executorService.submit(new Runnable() {
            @Override
            public void run() {
                loadToQueues(latestSnapshot, nextQ);
            }
        });

        int delCount = 0, newCount = 0;
        try (
                BufferedWriter newWriter = new BufferedWriter(new FileWriter(newOrUpdated));
                BufferedWriter delWriter = new BufferedWriter(new FileWriter(deleted))) {

            Line p = prevQ.take();
            Line n = nextQ.take();

            while (true) {
                if (p.equals(POISON) && n.equals(POISON)) {
                    log.info("both qs empty. breaking");
                    break;
                }
                if (p.equals(POISON) && !n.equals(POISON)) {
                    // write remainder of nextQ to new
                    newWriter.write(n.getAcc() + System.lineSeparator());
                    newCount++;
                    n = nextQ.take();
                    continue;
                }
                if (n.equals(POISON) && !p.equals(POISON)) {
                    delWriter.write(p.getAcc() + System.lineSeparator());
                    delCount++;
                    p = prevQ.take();
                    continue;
                }
                if (p.equals(n)) {
                    // in sync
                } else {
                    int compare = p.getAcc().compareTo(n.getAcc());
                    if (compare == 0) {
                        // acc is same. date changed. continue both queues
                        newWriter.write(p.getAcc() + System.lineSeparator());
                        newCount++;
                    } else if (compare > 0) {
                        newWriter.write(n.getAcc() + System.lineSeparator());
                        newCount++;
                        n = nextQ.take();
                        continue;
                    } else if (compare < 0) {
                        delWriter.write(p.getAcc() + System.lineSeparator());
                        delCount++;
                        p = prevQ.take();
                        continue;
                    }
                }
                p = prevQ.take();
                n = nextQ.take();
            }
        }
        log.info("shutting down");
        executorService.shutdown();
        log.info("new records found:{}", newCount);
        log.info("records to be deleted:{}", delCount);
        return new DiffFiles(newOrUpdated, deleted);
    }

    @SneakyThrows
    private boolean loadToQueues(File snapshot, BlockingQueue<Line> queue) {
        log.info("reading from:{}", snapshot);
        DateFormat LAST_UPDATED_DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
        long count = 0;
        try {
            try (BufferedReader reader = new BufferedReader(new FileReader(snapshot))) {
                String line = reader.readLine();
                if (StringUtils.isNotBlank(line)) {
                    if (line.startsWith("accession")) {
                        // skip
                    } else {
                        count++;
                        queue.put(Line.of(line, LAST_UPDATED_DATE_FORMAT));
                    }
                }
                while ((line = reader.readLine()) != null) {
                    count++;
                    if (count % 100000000 == 0) {
                        log.info("read {} from {}: {}", count, snapshot.getName(), line);
                    }
                    queue.put(Line.of(line, LAST_UPDATED_DATE_FORMAT));
                }
            }
            log.info("{} added. poisoning:{}", count, snapshot.getName());

            return true;
        } catch (Exception e) {
            log.error(snapshot.getName() + " Error:", e);
            return false;
        } finally {
            queue.put(POISON);
        }
    }


    @SneakyThrows
    public void downloadData(File newOrChangedList, String format, boolean annotationOnly) {
        String req = String.format(BROWSER_API_EMBL, format);

        final List<String> lines = Files.readAllLines(Paths.get(newOrChangedList.getAbsolutePath()));
        log.info("downloading for:{} records in {}", lines.size(), newOrChangedList.getAbsolutePath());
        File dataFile = new File(StringUtils.substringBeforeLast(newOrChangedList.getAbsolutePath(), ".") + ".dat");
        if (dataFile.exists()) {
            dataFile.delete();
        }
        log.info("writing to:{}", dataFile.getAbsolutePath());
        List<List<String>> subSets = ListUtils.partition(lines, 1000);
        try (BufferedOutputStream bw = new BufferedOutputStream(new FileOutputStream(dataFile))) {
            subSets.stream().map(s -> StringUtils.join(s, ",")).forEach(s -> {
                log.info("downloading:{}-{}", StringUtils.substringBefore(s,","), StringUtils.substringAfterLast(s,","));
                try {
                    String url = req + s;
                    if ("embl".equalsIgnoreCase(format) && annotationOnly) {
                        url += "?annotationOnly=true";
                    }
//                    log.info("req:{}", url);
                    HttpURLConnection connection = (HttpURLConnection) new URL(url).openConnection();
                    InputStream inputStream = connection.getInputStream();
                    IOUtils.copy(inputStream, bw);
                } catch (IOException e) {
                    log.error("Failed:" + BROWSER_API_EMBL + s, e);
                }
            });
        }
    }
}
