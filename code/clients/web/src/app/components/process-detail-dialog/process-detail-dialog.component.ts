import { Component, OnInit, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material';
import { Process } from 'app/models/Process';

@Component({
  selector: 'app-process-detail-dialog',
  templateUrl: './process-detail-dialog.component.html',
  styleUrls: ['./process-detail-dialog.component.scss']
})
export class ProcessDetailDialogComponent implements OnInit {

  constructor( @Inject(MAT_DIALOG_DATA) public process: Process) {

  }

  ngOnInit() {
  }

}
