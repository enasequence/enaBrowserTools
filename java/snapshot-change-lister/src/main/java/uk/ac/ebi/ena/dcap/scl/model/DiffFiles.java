package uk.ac.ebi.ena.dcap.scl.model;

import lombok.AllArgsConstructor;
import lombok.Getter;

import java.io.File;

@Getter
@AllArgsConstructor
public class DiffFiles {

    private File newOrChangedList;
    private File deletedList;

}
