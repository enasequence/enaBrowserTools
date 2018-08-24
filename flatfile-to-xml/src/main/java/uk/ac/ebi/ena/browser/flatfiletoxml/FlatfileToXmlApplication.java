package uk.ac.ebi.ena.browser.flatfiletoxml;

import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.Banner;
import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import uk.ac.ebi.embl.api.entry.Entry;
import uk.ac.ebi.embl.flatfile.reader.embl.EmblEntryReader;
import uk.ac.ebi.embl.flatfile.writer.xml.XmlEntryWriter;

import javax.validation.constraints.Pattern;
import java.io.*;

@Slf4j
@SpringBootApplication
public class FlatfileToXmlApplication implements CommandLineRunner {

    @Value("${flatfile}")
    String flatfile;

    @Value("${xmlfile}")
    String xmlfile;

    @Pattern(regexp = "(CDS|EMBL|MASTER|NCR|)")
    @Value("${format:#{null}}")
    String inputFormat;

    public static void main(String[] args) {
        SpringApplication app = new SpringApplication(FlatfileToXmlApplication.class);
        app.setBannerMode(Banner.Mode.OFF);
        app.run(args);
    }

    @Override
    public void run(String... args) throws Exception {
        log.info("Converting file {}", flatfile);
        String valid = validateArguments();
        if (StringUtils.isNotBlank(valid)) {
            log.info("Unable to process: {}", valid);
            System.out.println("Unable to process:" + valid);
            System.out.println("Usage: <flatfile path> <xml output path> <flatfile format: EMBL/CDS/NCR/MASTER>");
            System.out.println("Last argument is optional. Default format is EMBL.");
            System.out.println("e.g.");
            System.out.println("./ff-to-xml.sh /home/user/ABC.txt /home/user/ABC.xml CDS");
            System.out.println("ff-to-xml.bat c:\\user\\ABC.txt c:\\user\\ABC.xml");
            System.exit(1);
        }
        File file = new File(flatfile);
        File outputFile = new File(xmlfile);
        EmblEntryReader.Format format = EmblEntryReader.Format.EMBL_FORMAT;
        if (StringUtils.isNotBlank(inputFormat)) {
            format = EmblEntryReader.Format.valueOf(inputFormat + "_FORMAT");
        }
        try (
                BufferedReader fileReader = new BufferedReader(new FileReader(file));
                BufferedWriter writer = new BufferedWriter(new FileWriter(outputFile))) {
            EmblEntryReader reader = new EmblEntryReader(fileReader,
                    format, file.getName());
            reader.read();
            Entry entry = reader.getEntry();
            writer.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + System.lineSeparator());
            new XmlEntryWriter(entry).write(writer);
        }
    }

    private String validateArguments() {
        if (StringUtils.isBlank(flatfile) || !new File(flatfile).exists()) {
            return "Please specify full path of flatfile.";
        }
        if (StringUtils.isBlank(xmlfile) || !new File(xmlfile).getParentFile().exists()) {
            return ("Please specify full path of xml output file.");
        }
        if (StringUtils.isBlank(inputFormat)) {
            log.info("Flatfile format not specified. Defaulting to EMBL format.");
        }
        return null;
    }
}
