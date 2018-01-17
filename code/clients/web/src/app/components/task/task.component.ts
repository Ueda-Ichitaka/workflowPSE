import { Component, OnInit, HostBinding, Input, ElementRef, Output, EventEmitter, HostListener } from '@angular/core';
import { MatDialog, MatMenu, MatMenuTrigger } from '@angular/material';
import { ProcessParameterType, ProcessParameter } from 'app/models/ProcessParameter';
import { ViewChild } from '@angular/core';
import { ProcessDetailDialogComponent } from 'app/components/process-detail-dialog/process-detail-dialog.component';
import { Process } from 'app/models/Process';
import { LocaleDataIndex } from '@angular/common/src/i18n/locale_data';
import { Task } from 'app/models/Task';
import { ArtefactDialogComponent } from 'app/components/artefact-dialog/artefact-dialog.component';

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

  @ViewChild(MatMenuTrigger)
  public menuComponent: MatMenuTrigger;

  @Output()
  public parameterDrag = new EventEmitter<ProcessParameter<'input' | 'output'>>();

  @Output()
  public parameterDrop = new EventEmitter<ProcessParameter<'input' | 'output'>>();

  @Output()
  public taskRemove = new EventEmitter<Task>();

  private mouseDownPos: number[];

  public constructor(public dialog: MatDialog, private el: ElementRef) { }

  public ngOnInit() {

  }


  @HostListener('mousedown', ['$event'])
  public hostMouseDown(event: MouseEvent) {
    this.mouseDownPos = [event.pageX, event.pageY];
  }

  @HostListener('mouseup', ['$event'])
  public hostMouseUp(event: MouseEvent) {
    if ((<HTMLElement>event.target).classList.contains('nomove')) {
      return;
    }
    if (this.mouseDownPos && this.mouseDownPos[0] === event.pageX && this.mouseDownPos[1] === event.pageY) {
      this.menuComponent.openMenu();
    }
    this.mouseDownPos = undefined;
  }

  public clickDelete() {
    this.taskRemove.emit(this.task);
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

  public parameterMouseDown(parameter: ProcessParameter<'input' | 'output'>, event: MouseEvent) {
    this.mouseDownPos = [event.pageX, event.pageY];
    this.parameterDrag.emit(parameter);
  }

  public parameterMouseUp(parameter: ProcessParameter<'input' | 'output'>, event: MouseEvent) {
    if (this.mouseDownPos && this.mouseDownPos[0] === event.pageX && this.mouseDownPos[1] === event.pageY) {
      this.dialog.open(ArtefactDialogComponent, {
        data: parameter
      });
    }
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
