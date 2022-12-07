package uk.ac.ebi.ena.browser.service;

import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import uk.ac.ebi.ena.browser.dao.EraDao;
import uk.ac.ebi.ena.browser.model.Submission;

import java.time.LocalDateTime;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.LinkedBlockingQueue;

@Service
@Slf4j
public class ReaderService {

    private final EraDao eraDao;

    public ReaderService(EraDao eraDao) {
        this.eraDao = eraDao;
    }

    @Async
    public CompletableFuture<Boolean> read(LinkedBlockingQueue<Submission> queue, LocalDateTime lastIndex) {
        try {
            log.info("Started reading ...");
            return this.eraDao.getSubmission(queue, lastIndex);
        } catch (Exception e) {
            log.error("Error reading", e);
            return CompletableFuture.completedFuture(false);
        }
    }
}
