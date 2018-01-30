import { Component, OnInit, Input, ElementRef, Output, EventEmitter, HostListener } from '@angular/core';
import { MatDialog, MatMenu, MatMenuTrigger } from '@angular/material';
import { ProcessParameterType, ProcessParameter } from 'app/models/ProcessParameter';
import { ViewChild } from '@angular/core';
import { ProcessDialogComponent } from 'app/components/process-dialog/process-dialog.component';
import { Process } from 'app/models/Process';
import { Task, TaskState } from 'app/models/Task';
import { ArtefactDialogComponent } from 'app/components/artefact-dialog/artefact-dialog.component';

export interface TaskParameterTuple {
  task: Task;
  parameter: ProcessParameter<'input' | 'output'>;
}

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

  @Output()
  public changeArtefact = new EventEmitter<[TaskParameterTuple, object]>();

  @Input()
  public showState = false;

  private mouseDownPos: number[];

  public constructor(public dialog: MatDialog, private el: ElementRef) { }

  public ngOnInit() {

  }

  public get stateInfo(): { name: string, color: string } {
    const infoMap = [
      { state: TaskState.DEPRECATED, name: 'DEPRECATED', color: '#E91E63' },
      { state: TaskState.FAILED, name: 'FAILED', color: '#F44336' },
      { state: TaskState.FINISHED, name: 'FINISHED', color: '#2196F3' },
      { state: TaskState.READY, name: 'READY', color: '#03A9F4' },
      { state: TaskState.RUNNING, name: 'RUNNING', color: '#FFC107' },
      { state: TaskState.WAITING, name: 'WAITING', color: '#9E9E9E' },
    ];

    return infoMap.find(info => info.state === this.task.state);
  }

  @HostListener('mousedown', ['$event'])
  public hostMouseDown(event: MouseEvent) {
    if (event.button === 0) {
      this.mouseDownPos = [event.pageX, event.pageY];
    }
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

  @HostListener('contextmenu', ['$event'])
  public hostContextmenu(event: MouseEvent) {
    this.menuComponent.openMenu();
    return false;
  }

  public clickDelete() {
    this.taskRemove.emit(this.task);
  }

  public openDetail() {
    this.dialog.open(ProcessDialogComponent, {
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
    if (this.hasArtefact(parameter)) {
      return;
    }

    this.mouseDownPos = [event.pageX, event.pageY];
    this.parameterDrag.emit(parameter);
  }

  public parameterMouseUp(parameter: ProcessParameter<'input' | 'output'>, event: MouseEvent) {
    if (this.mouseDownPos && this.mouseDownPos[0] === event.pageX && this.mouseDownPos[1] === event.pageY) {
      this.dialog.open(ArtefactDialogComponent, {
        data: {
          task: this,
          parameter
        }
      });
    } else {
      if (!this.hasArtefact(parameter)) {
        this.parameterDrop.emit(parameter);
      }
    }
  }

  public addArtefact(parameter: ProcessParameter<'input' | 'output'>, data: object) {
    this.changeArtefact.emit([{ task: this.task, parameter }, data]);
  }

  public hasArtefact(parameter: ProcessParameter<'input' | 'output'>) {
    if (!this.task.input_artefacts) {
      return;
    }
    const index = this.task.input_artefacts.findIndex(artefact => artefact.parameter_id === parameter.id);
    return index !== -1;
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
