import { Component, OnInit, HostBinding, Input, ElementRef, Output, EventEmitter } from '@angular/core';
import { MatDialog } from '@angular/material';
import { ProcessParameterType, ProcessParameter } from 'app/models/ProcessParameter';
import { HostListener } from '@angular/core/src/metadata/directives';
import { ViewChild } from '@angular/core';
import { ProcessDetailDialogComponent } from 'app/components/process-detail-dialog/process-detail-dialog.component';
import { Process } from 'app/models/Process';
import { LocaleDataIndex } from '@angular/common/src/i18n/locale_data';
import { Task } from 'app/models/Task';

@Component({
  selector: 'app-task',
  templateUrl: './task.component.html',
  styleUrls: ['./task.component.scss']
})
export class TaskComponent implements OnInit {

  @Input()
  public process: Process;

  @Input()
  public task: Task;

  @ViewChild('inputs')
  public inputContainer: ElementRef;

  @ViewChild('outputs')
  public outputContainer: ElementRef;

  @Output()
  public parameterDrag = new EventEmitter<ProcessParameter<'input' | 'output'>>();

  @Output()
  public parameterDrop = new EventEmitter<ProcessParameter<'input' | 'output'>>();

  public constructor(public dialog: MatDialog, private el: ElementRef) { }

  public ngOnInit() {

  }

  public openDetail() {
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

  public parameterMouseDown(parameter: ProcessParameter<'input' | 'output'>) {
    this.parameterDrag.emit(parameter);
  }

  public parameterMouseUp(parameter: ProcessParameter<'input' | 'output'>) {
    this.parameterDrop.emit(parameter);
  }


  public getParameterPosition(role: 'input' | 'output', id: number): [number, number] {
    const n: HTMLDivElement = (role === 'input' ? this.inputContainer : this.outputContainer).nativeElement;

    for (let i = 0; i < n.childElementCount; i++) {
      if (n.children[i].getAttribute('data-id') === '' + id) {
        const rect = n.children[i].getBoundingClientRect();
        return [rect.left + 11, rect.top + 11];
      }
    }
    return null;
  }

}
