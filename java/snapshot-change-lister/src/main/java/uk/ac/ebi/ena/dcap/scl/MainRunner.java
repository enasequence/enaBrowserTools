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
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;
import uk.ac.ebi.ena.dcap.scl.model.DataType;
import uk.ac.ebi.ena.dcap.scl.service.MainService;

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

    @Autowired
    private MainService mainService;

    @Override
    public void run(String... args) {
        DataType dataType = DataType.valueOf(dataTypeStr);
        File prevSnapshot = new File(previousSnapshotPath);
        assert prevSnapshot.exists();
        File outputLocation = new File(outputLocationPath);
        assert outputLocation.canWrite();

        String name = dataType.name().toLowerCase() + "_" + DATE_FORMAT.format(new Date());
        File newSnapshot = mainService.writeLatestSnapshot(dataType, outputLocation, name);
        mainService.compareSnapshots(prevSnapshot, newSnapshot, outputLocation, name);
    }
}
