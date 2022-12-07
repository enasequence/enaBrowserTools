package uk.ac.ebi.ena.browser.service;

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;
import uk.ac.ebi.ena.browser.model.Submission;

import java.sql.ResultSet;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.LinkedBlockingQueue;

@Service
@Slf4j
public class SampleConverter {

    private final Submission POISON = Submission.getPoison();

    @SneakyThrows
    @Async
    public CompletableFuture<Boolean> convertAndQueue(LinkedBlockingQueue<Submission> queue, ResultSet resultSet, long count) {
        try {
            log.info("isAfterLast: {}", resultSet.isAfterLast());
            if (!resultSet.isAfterLast()) {
                log.info("Converting > {}, {}", count, resultSet.getString("submission_id"));
                Submission submission = Submission.builder()
                        .submissionId(resultSet.getString("submission_id"))
                        .submissionAlias(resultSet.getString("submission_alias"))
                        .firstCreated(resultSet.getTimestamp("first_created").toLocalDateTime())
                        .build();
                log.info("Converted {}", submission.getSubmissionId());
                queue.put(submission);
            }
        } catch (Exception e) {
            log.error("Error during conversion: ", e);
            return CompletableFuture.completedFuture(false);
        }
        return CompletableFuture.completedFuture(true);
    }

    @SneakyThrows
    public void addPoison(LinkedBlockingQueue<Submission> queue) {
        log.info("Adding poison {}", POISON.getSubmissionId());
        queue.put(POISON);
        log.info("Added poison {}", POISON.getSubmissionId());
    }
}
