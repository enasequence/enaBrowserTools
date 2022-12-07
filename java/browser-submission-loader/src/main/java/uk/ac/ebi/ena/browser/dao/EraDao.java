package uk.ac.ebi.ena.browser.dao;

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Qualifier;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Repository;
import uk.ac.ebi.ena.browser.model.Submission;

import java.sql.ResultSet;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicLong;

@Repository
@Slf4j
public class EraDao {

    public static final int MILLION = 1000000;

    private final Submission POISON = Submission.getPoison();

    private final JdbcTemplate eraproJdbcTemplate;

    public EraDao(@Qualifier("jdbcErapro") JdbcTemplate eraproJdbcTemplate) {
        this.eraproJdbcTemplate = eraproJdbcTemplate;
    }

    @SneakyThrows
    @Async
    public CompletableFuture<Boolean> getSubmission(LinkedBlockingQueue<Submission> queue, LocalDateTime lastIndex) {
        String sqlQuery = """
                select submission_id, submission_alias, first_created
                from era.submission
                """;
        AtomicLong count = new AtomicLong(0);
        try {
            if (null != lastIndex) {
                String lastIndexStr = lastIndex.format(DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss"));
                sqlQuery = sqlQuery + " where first_created > to_date('" + lastIndexStr + "', 'YYYY-MM-DD HH24:MI:SS')";
            }
            log.info("Getting submission:{}", sqlQuery);
            eraproJdbcTemplate.query(sqlQuery, new RowMapper<>() {
                @SneakyThrows
                @Override
                public CompletableFuture<Boolean> mapRow(ResultSet resultSet, int rowNum) {
                    count.getAndIncrement();
                    Submission submission = Submission.builder()
                            .submissionId(resultSet.getString("submission_id"))
                            .submissionAlias(resultSet.getString("submission_alias"))
                            .firstCreated(resultSet.getTimestamp("first_created").toLocalDateTime())
                            .build();
                    queue.put(submission);
                    if (count.get() % MILLION == 0) {
                        log.info("{} read", count.get());
                    }
                    return null;
                }
            });
        } finally {
            log.info("Adding poison after reading {} submission records", count.get());
            queue.put(POISON);
        }
        return CompletableFuture.completedFuture(true);
    }
}
