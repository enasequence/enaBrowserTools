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

import lombok.NoArgsConstructor;
import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.lang3.StringUtils;
import org.apache.commons.lang3.exception.ExceptionUtils;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.mail.javamail.JavaMailSender;
import org.springframework.mail.javamail.MimeMessagePreparator;
import org.springframework.stereotype.Component;
import uk.ac.ebi.ena.dcap.scl.model.DataType;
import uk.ac.ebi.ena.dcap.scl.model.DiffFiles;
import uk.ac.ebi.ena.dcap.scl.service.MainService;

import javax.mail.Message;
import javax.mail.MessagingException;
import javax.mail.internet.InternetAddress;
import javax.mail.internet.MimeMessage;
import java.io.File;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;

@Component
@Slf4j
@NoArgsConstructor
public class MainRunner implements CommandLineRunner {

    public static final DateFormat DATE_FORMAT = new SimpleDateFormat("yyyyMMdd");

    @Value("${dataType}")
    public String dataTypeStr;

    @Value("${previousSnapshot}")
    public String previousSnapshotPath;

    @Value("${outputLocation}")
    public String outputLocationPath;

    @Value("${email:#{null}}")
    public String email;

    @Value("${query:#{null}}")
    public String query;

    @Value("${downloadData:#{false}}")
    public boolean downloadData;

    @Value("${annotationOnly:#{false}}")
    public boolean annotationOnly;

    @Value("${format:embl}")
    public String format;

    @Autowired
    private MainService mainService;

    @Autowired
    JavaMailSender mailSender;

    @SneakyThrows
    @Override
    public void run(String... args) {
        DataType dataType = DataType.valueOf(dataTypeStr);
        File prevSnapshot = new File(previousSnapshotPath);
        assert prevSnapshot.exists();
        File outputLocation = new File(outputLocationPath);
        assert outputLocation.canWrite();

        String name = dataType.name().toLowerCase() + "_" + DATE_FORMAT.format(new Date());
        try {
            File newSnapshot = mainService.writeLatestSnapshot(dataType, outputLocation, name, query);
            final DiffFiles diffFiles = mainService.compareSnapshots(prevSnapshot, newSnapshot, outputLocation, name);
            if (downloadData) {
                mainService.downloadData(diffFiles.getNewOrChangedList(), format, annotationOnly);
            }
            if (StringUtils.isNotBlank(email)) {
                sendMail(email, dataTypeStr + " change lister completed",
                        "Compared " + prevSnapshot + " & " + newSnapshot + " in " + outputLocation);
            }
        } catch (Exception e) {
            log.error("error:", e);
            if (StringUtils.isNotBlank(email)) {
                sendMail(email, dataTypeStr + " change lister failed", ExceptionUtils.getStackTrace(e));
            }
        }
    }

    public void sendMail(String email, String subject, String body, String... args) throws MessagingException {
        MimeMessagePreparator preparator = new MimeMessagePreparator() {

            public void prepare(MimeMessage mimeMessage) throws Exception {

                mimeMessage.setRecipient(Message.RecipientType.TO,
                        new InternetAddress(email));
                mimeMessage.setFrom(new InternetAddress("datalib@ebi.ac.uk"));
                mimeMessage.setText(body
                        + System.lineSeparator() + StringUtils.join(args, " "));
                mimeMessage.setSubject(subject);
            }
        };

        try {
            mailSender.send(preparator);
        } catch (Exception ex) {
            // simply log it and go on...
            log.error("Error sending email", ex);
        }
    }
}
