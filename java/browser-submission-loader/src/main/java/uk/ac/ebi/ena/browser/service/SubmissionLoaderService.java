package uk.ac.ebi.ena.browser.service;

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import uk.ac.ebi.ena.browser.dao.EtaDao;
import uk.ac.ebi.ena.browser.model.Submission;

import java.time.LocalDateTime;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.stream.Collectors;

@Service
@Slf4j
public class SubmissionLoaderService {

    private static final int CHUNK_SIZE = 50000;
    private final LinkedBlockingQueue<Submission> queue = new LinkedBlockingQueue<>(CHUNK_SIZE);

    private final EtaDao etaDao;

    private final ReaderService readerService;

    private final WriterService writerService;

    public SubmissionLoaderService(EtaDao etaDao, ReaderService readerService, WriterService writerService) {
        this.etaDao = etaDao;
        this.readerService = readerService;
        this.writerService = writerService;
    }

    @SneakyThrows
    public void process() {
        LocalDateTime lastIndex = etaDao.getLastIndex();
        CompletableFuture<Boolean> readFuture = readerService.read(queue, lastIndex);
        CompletableFuture<Boolean> writeFuture = writerService.write(queue);
        SubmissionLoaderService.waitForAllWorkers("Reader ", Collections.singletonList(readFuture), true);
        SubmissionLoaderService.waitForAllWorkers("Writer", Collections.singletonList(writeFuture), true);
    }

    @SneakyThrows
    public static void waitForAllWorkers(String msg, List<CompletableFuture<Boolean>> completableFutures,
                                         boolean logMessage) {
        if (logMessage) {
            log.info("{} waiting for {} workers", msg, completableFutures.size());
        }

        if (completableFutures.isEmpty()) {
            log.info("no completable futures. returning");
            return;
        }
        /* Returns a new CompletableFuture that is completed when all the given CompletableFutures
                    complete.*/
        CompletableFuture<Void> readFutures =
                CompletableFuture.allOf(completableFutures.toArray(new CompletableFuture[0]));

        /* Returns a new CompletableFuture that is completed when all the given CompletableFutures
        complete with return value*/
        CompletableFuture<List<Boolean>> allCompletableFuture =
                readFutures.thenApply(future -> completableFutures.stream().map(CompletableFuture::join).collect
                        (Collectors.toList()));
        allCompletableFuture.join();
        for (CompletableFuture<Boolean> f : completableFutures) {
            if (!f.get()) {
                throw new Exception("future failure");
            }
        }
        if (logMessage) {
            log.info("{} all workers done", msg);
        }
    }
}
