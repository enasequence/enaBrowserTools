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
package uk.ac.ebi.ena.dcap.scl;

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;
import uk.ac.ebi.ena.dcap.scl.model.DataType;
import uk.ac.ebi.ena.dcap.scl.model.Line;

import java.io.*;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.concurrent.*;

import static uk.ac.ebi.ena.dcap.scl.model.Line.POISON;

@Service
@Slf4j
public class MainService {

    final ExecutorService executorService = Executors.newFixedThreadPool(2);

    @Autowired
    RestClient restClient;

    public File writeLatestSnapshot(DataType dataType, File outputLocation, String fileName) {

        File outFile = new File(outputLocation.getAbsolutePath() + File.separator + fileName + ".tsv");
        if (outFile.exists()) {
            outFile.delete();
        }
        return restClient.getLatestSnapshot(dataType, outFile);
    }

    @SneakyThrows
    public void compareSnapshots(File previousSnapshot, File latestSnapshot, File outputLocation, String namePrefix) {
        File newOrUpdated = new File(outputLocation.getAbsolutePath() + File.separator + namePrefix + "_new-or-updated.tsv");
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

        try (
             BufferedWriter newWriter = new BufferedWriter(new FileWriter(newOrUpdated));
             BufferedWriter delWriter = new BufferedWriter(new FileWriter(deleted))) {

            Line p = prevQ.take();
            Line n = nextQ.take();

            while (true) {
                if (p.equals(POISON) && n.equals(POISON)) {
                    break;
                }
                if (p.equals(POISON) && !n.equals(POISON)) {
                    // write remainder of nextQ to new
                    newWriter.write(n.getAcc() + System.lineSeparator());
                    n = nextQ.take();
                    continue;
                }
                if (n.equals(POISON) && !p.equals(POISON)) {
                    delWriter.write(p.getAcc() + System.lineSeparator());
                    p = prevQ.take();
                    continue;
                }
                if (p.equals(n)) {
                    // in sync
                } else {
                    switch (p.getAcc().compareTo(n.getAcc())) {
                        case 0: // acc is same. date changed. continue both queues
                            newWriter.write(p.getAcc() + System.lineSeparator());
                            break;
                        case 1:
                            newWriter.write(n.getAcc() + System.lineSeparator());
                            n = nextQ.take();
                            continue;
                        case -1:
                            delWriter.write(p.getAcc() + System.lineSeparator());
                            p = prevQ.take();
                            continue;
                    }
                }
                p = prevQ.take();
                n = nextQ.take();
            }
        }
        executorService.shutdown();
    }

    @SneakyThrows
    private void loadToQueues(File snapshot, BlockingQueue<Line> queue) {
        DateFormat LAST_UPDATED_DATE_FORMAT = new SimpleDateFormat("yyyy-MM-dd");
        try (BufferedReader reader = new BufferedReader(new FileReader(snapshot))) {
            String line = reader.readLine();
            if (StringUtils.isNotBlank(line)) {
                if (line.startsWith("accession")) {
                    // skip
                } else {
                    queue.put(Line.of(line, LAST_UPDATED_DATE_FORMAT));
                }
            }
            while ((line = reader.readLine()) != null) {
                queue.put(Line.of(line, LAST_UPDATED_DATE_FORMAT));
            }
            queue.put(POISON);
        }
    }

}
