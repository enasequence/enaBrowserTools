package uk.ac.ebi.ena.browser.service;

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import uk.ac.ebi.ena.browser.dao.EtaDao;
import uk.ac.ebi.ena.browser.model.Submission;

import java.util.ArrayList;
import java.util.LinkedList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.LinkedBlockingQueue;

@Service
@Slf4j
public class WriterService {

    private static final int INSERT_BATCH_SIZE = 5000;
    private final EtaDao etaDao;

    public WriterService(EtaDao etaDao) {
        this.etaDao = etaDao;
    }

    @SneakyThrows
    @Async
    public CompletableFuture<Boolean> write(LinkedBlockingQueue<Submission> queue) {
        try {
            log.info("Started writing ... ");
            List<Submission> submissions = new ArrayList<>();
            List<CompletableFuture<Boolean>> insertFutures = new LinkedList<>();

            int counter = 0;
            boolean poisoned = false;
            while (!poisoned) {
                final Submission submission = queue.take();
                if (submission.isPoison()) {
                    poisoned = true;
                    log.info("poison found with {} submission pending to insert", submissions.size());
                    if (submissions.size() > 0) {
                        final CompletableFuture<Boolean> insertBatch = etaDao.insertSamples(submissions);
                        insertFutures.add(insertBatch);
                    }
                } else {
                    counter++;
                    submissions.add(submission);
                    if (counter == INSERT_BATCH_SIZE) {
                        insertFutures.add(etaDao.insertSamples(submissions));
                        counter = 0;
                        submissions = new ArrayList<>();
                    }
                }
            }
            SubmissionLoaderService.waitForAllWorkers("Batch Inserter", insertFutures, true);
        } catch (Exception e) {
            log.error("Error during insertion: ", e);
            return CompletableFuture.completedFuture(false);
        }
        return CompletableFuture.completedFuture(true);
    }

}
