import { Component, OnInit, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material';
import { Process } from 'app/models/Process';
import { ProcessParameterType } from 'app/models/ProcessParameter';
import { ProcessService } from 'app/services/process.service';

@Component({
  selector: 'app-process-dialog',
  templateUrl: './process-dialog.component.html',
  styleUrls: ['./process-dialog.component.scss']
})
export class ProcessDialogComponent implements OnInit {

  constructor( @Inject(MAT_DIALOG_DATA) public process: Process) {

  }

  ngOnInit() {
  }

  public getTypeName(type: ProcessParameterType) {
    return ProcessService.getTypeName(type);
  }

  public getTypeColor(type: ProcessParameterType) {
    return ProcessService.getTypeColor(type);
  }
}
