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

import lombok.SneakyThrows;
import lombok.extern.slf4j.Slf4j;
import org.apache.commons.io.IOUtils;
import org.springframework.stereotype.Component;
import uk.ac.ebi.ena.dcap.scl.model.DataType;

import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.URL;

@Component
@Slf4j
public class RestClient {

    static final String URL = "https://www.ebi.ac.uk/ena/portal/api/search?result=%s&fields=accession," +
            "last_updated&sortFields=accession&limit=0";

    @SneakyThrows
    public File getLatestSnapshot(DataType dataType, File outputFile) {
        URL url = new URL(String.format(URL, dataType.name().toLowerCase()));
        try (InputStream in = url.openStream();
             OutputStream out = new FileOutputStream(outputFile)) {
            IOUtils.copyLarge(in, out);
        }
        return outputFile;
    }
}
