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
package uk.ac.ebi.ena.dcap.scl.model;

import lombok.AllArgsConstructor;
import lombok.EqualsAndHashCode;
import lombok.Getter;
import lombok.SneakyThrows;
import org.apache.commons.lang3.StringUtils;

import java.text.DateFormat;
import java.util.Date;

@Getter
@AllArgsConstructor
@EqualsAndHashCode
public class Line {

    public static Line POISON = new Line(null, null);

    private String acc;
    private Date lastUpdated;

    @SneakyThrows
    public static Line of(String s, DateFormat df) {
        final String[] split = StringUtils.split(s);
        if (split.length == 2) {
            return new Line(split[0], df.parse(split[1]));
        } else {
            return new Line(split[0], null);
        }
    }
}
