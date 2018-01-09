import { Component, OnInit, Inject } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material';

@Component({
  selector: 'app-process-detail-dialog',
  templateUrl: './process-detail-dialog.component.html',
  styleUrls: ['./process-detail-dialog.component.scss']
})
export class ProcessDetailDialogComponent implements OnInit {

  constructor( @Inject(MAT_DIALOG_DATA) public data: any) {
    console.log(data);
  }

  ngOnInit() {
  }

}
