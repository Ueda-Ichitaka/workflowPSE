import { Component, OnInit, HostListener, ElementRef, Input } from '@angular/core';
import { Process } from 'app/models/Process';
import { ViewChild } from '@angular/core';
import { Workflow } from 'app/models/Workflow';
import { Task, TaskState } from 'app/models/Task';

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  styleUrls: ['./editor.component.scss']
})
export class EditorComponent implements OnInit {

  public edges: {
    a: Process;
    b: Process;
    input_id: number;
    output_id: number;
  };

  public edgePaths: {
    xa: number;
    ya: number;
    xb: number;
    yb: number;
    xc: number;
    yc: number;
  }[];

  private movement = {
    index: null,
    x: null,
    y: null
  };

  @Input()
  public workflow: Workflow;

  @Input()
  public processes: Process[];

  @ViewChild('background')
  public background: ElementRef;

  public constructor(private el: ElementRef) {

  }

  ngOnInit() {
    // Create initial workflow if no workflow is provided
    if (!this.workflow) {
      this.workflow = {
        id: -1,
        title: 'my Workflow',
        edges: [],
        tasks: [],
        creator_id: -1,
        shared: false,
        created_at: -1,
        updated_at: -1
      };
    }
  }

  public svgPath(e) {
    return `M ${e.xa} ${e.ya} q ${e.xb} ${e.yb} ${e.xc} ${e.yc}`;
  }

  public add(process: Process, x: number, y: number) {
    const timestamp = (new Date()).getTime();

    // create task
    const task: Task = {
      id: -1,
      x,
      y,
      state: TaskState.READY,
      process_id: process.id,
      input_artefacts: [],
      ouput_artefacts: [],
      created_at: timestamp,
      updated_at: timestamp,
    };

    // add task to current workflow
    this.workflow.tasks.push(task);
  }

  public findProcess(id: number): Process {
    return this.processes.find(process => process.id === id);
  }


  public dragStart(index: number, event: MouseEvent) {
    // store index of moved task
    this.movement = { index, x: event.offsetX, y: event.offsetY };
  }

  @HostListener('mousemove', ['$event'])
  public dragMove(event: MouseEvent) {
    // return if no task is selected
    if (this.movement.index === null) { return; }

    // get movement data
    const { index, x, y } = this.movement;
    const n: HTMLElement = this.el.nativeElement;
    const r = n.getBoundingClientRect();

    // calcualte new position
    this.workflow.tasks[index].x = event.pageX + n.scrollLeft - r.left - x;
    this.workflow.tasks[index].y = event.pageY + n.scrollTop - r.top - y - 20;
  }

  @HostListener('mouseup')
  public dragEnd(event) {
    // reset movement data
    this.movement.index = null;
  }

  public dragOver(event: DragEvent): boolean {
    // this needs to return false validate dropping area
    return false;
  }

  public drop(event: DragEvent) {
    // get process data from drag and drop event
    const process: Process = JSON.parse(event.dataTransfer.getData('json'));
    // add process
    this.add(process, event.offsetX - 100, event.offsetY - 50);
  }

}
