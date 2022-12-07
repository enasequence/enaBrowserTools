package uk.ac.ebi.ena.browser.model;

import lombok.Builder;
import lombok.Getter;
import org.apache.commons.lang3.StringUtils;

import java.time.LocalDateTime;

@Builder
@Getter
public class Submission {

    private String submissionId;
    private String submissionAlias;
    private LocalDateTime firstCreated;

    public static Submission getPoison() {
        return Submission.builder().submissionId(null).build();
    }

    public boolean isPoison() {
        return StringUtils.isBlank(this.getSubmissionId());
    }
}
