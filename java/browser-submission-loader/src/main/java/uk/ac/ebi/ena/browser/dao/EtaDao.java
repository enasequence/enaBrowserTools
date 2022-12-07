package uk.ac.ebi.ena.browser.dao;

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Repository;
import uk.ac.ebi.ena.browser.model.Submission;

import java.sql.PreparedStatement;
import java.sql.Timestamp;
import java.time.LocalDateTime;
import java.util.List;
import java.util.concurrent.CompletableFuture;

@Repository
@Slf4j
public class EtaDao {

    private final JdbcTemplate etaproJdbcTemplate;

    public EtaDao(@Qualifier("jdbcEtapro") JdbcTemplate etaproJdbcTemplate) {
        this.etaproJdbcTemplate = etaproJdbcTemplate;
    }

    public LocalDateTime getLastIndex() {
        String sqlQuery = "select max(first_created) from eta.BROWSER_SUBMISSION";
        try {
            LocalDateTime localDateTime = etaproJdbcTemplate.queryForObject(sqlQuery, LocalDateTime.class);
            log.info("Last loaded Submission is at: {}", localDateTime);
            return localDateTime;
        } catch (Exception e) {
            log.warn("Error fetching last index time {}.\nContinue full load", e.getMessage());
        }
        return null;
    }

    @SneakyThrows
    public CompletableFuture<Boolean> insertSamples(List<Submission> submissions) {
        log.debug("Batch update {} submissions", submissions.size());
        etaproJdbcTemplate.batchUpdate("INSERT INTO eta.BROWSER_SUBMISSION (SUBMISSION_ID, SUBMISSION_ALIAS," +
                        " FIRST_CREATED) VALUES (?, ?, ?)",
                submissions,
                100,
                (PreparedStatement ps, Submission submission) -> {
                    ps.setString(1, submission.getSubmissionId());
                    ps.setString(2, submission.getSubmissionAlias());
                    ps.setTimestamp(3, Timestamp.valueOf(submission.getFirstCreated()));
                });
        return CompletableFuture.completedFuture(true);
    }
}
