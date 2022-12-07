package uk.ac.ebi.ena.browser.core;

import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.CommandLineRunner;
import org.springframework.scheduling.annotation.EnableAsync;
import org.springframework.stereotype.Component;
import uk.ac.ebi.ena.browser.service.SubmissionLoaderService;

@Component
@Slf4j
@EnableAsync
public class SampleLoader implements CommandLineRunner {

    private final SubmissionLoaderService submissionLoaderService;

    public SampleLoader(SubmissionLoaderService submissionLoaderService) {
        this.submissionLoaderService = submissionLoaderService;
    }

    @Override
    public void run(String... args) {
        try {
            submissionLoaderService.process();
            System.exit(0);
        } catch (Exception e) {
            log.error("Error: ", e);
            System.exit(-1);
        }
    }
}
