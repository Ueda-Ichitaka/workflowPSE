import { Component, OnInit, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material';
import { Artefact } from 'app/models/Artefact';
import { ProcessParameter } from 'app/models/ProcessParameter';

@Component({
  selector: 'app-artefact-dialog',
  templateUrl: './artefact-dialog.component.html',
  styleUrls: ['./artefact-dialog.component.scss']
})
export class ArtefactDialogComponent implements OnInit {

  constructor( @Inject(MAT_DIALOG_DATA) public parameter: ProcessParameter<'input' | 'output'>) {

  }

  ngOnInit() {
  }

}
