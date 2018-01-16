import { Component, OnInit, HostBinding, Input, ElementRef } from '@angular/core';
import { MatDialog } from '@angular/material';
import { ProcessParameterType } from 'app/models/ProcessParameter';
import { HostListener } from '@angular/core/src/metadata/directives';
import { ViewChild } from '@angular/core';
import { ProcessDetailDialogComponent } from 'app/components/process-detail-dialog/process-detail-dialog.component';
import { Process } from 'app/models/Process';

@Component({
  selector: 'app-task',
  templateUrl: './task.component.html',
  styleUrls: ['./task.component.scss']
})
export class TaskComponent implements OnInit {

  @Input()
  public process: Process;

  @ViewChild('inputs')
  public inputContainer: ElementRef;

  @ViewChild('outputs')
  public outputContainer: ElementRef;

  public constructor(public dialog: MatDialog, private el: ElementRef) { }

  public openDetailDialog() {
    this.dialog.open(ProcessDetailDialogComponent, {
      data: this.process
    });
  }

  public getParameterColor(type: ProcessParameterType): string {
    switch (type) {
      case ProcessParameterType.LITERAL: return '#03A9F4';
      case ProcessParameterType.COMPLEX: return '#FFC107';
      case ProcessParameterType.BOUNDING_BOX: return '#4CAF50';
      default: return '#000000';
    }
  }

  public ngOnInit() {

  }

  public getInputPosition(id: number): [number, number] {
    const n = (<HTMLDivElement>this.inputContainer.nativeElement);

    for (let i = 0; i < n.childElementCount; i++) {
      if (n.children[i].getAttribute('data-id') === '' + id) {
        const rect = n.children[i].getBoundingClientRect();
        return [rect.left, rect.top];
      }
    }

    return null;
  }

  public getOutputPosition(id: number): [number, number] {
    const n = (<HTMLDivElement>this.outputContainer.nativeElement);

    for (let i = 0; i < n.childElementCount; i++) {
      if (n.children[i].getAttribute('data-id') === '' + id) {
        const rect = n.children[i].getBoundingClientRect();
        return [rect.left, rect.top];
      }
    }

    return null;
  }
}
