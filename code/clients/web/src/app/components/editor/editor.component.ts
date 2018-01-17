import { Component, OnInit, HostListener, ElementRef, Input, QueryList, ViewChildren } from '@angular/core';
import { Process } from 'app/models/Process';
import { ViewChild } from '@angular/core';
import { Workflow } from 'app/models/Workflow';
import { Task, TaskState } from 'app/models/Task';
import { ProcessParameter } from 'app/models/ProcessParameter';
import { MediaQueryListListener } from '@angular/flex-layout';
import { TaskComponent } from 'app/components/task/task.component';

interface MovementData {
  edge?: [number, number, number, number];
  index?: number;
  x?: number;
  y?: number;
}

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  styleUrls: ['./editor.component.scss']
})
export class EditorComponent implements OnInit {

  @Input()
  public workflow: Workflow;

  @Input()
  public processes: Process[];

  private movement: MovementData = {};

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

  public getSvgEdge(edge: [number, number, number, number]) {
    // define bezier control points
    const c1 = [
      edge[0],
      edge[3]
    ];
    const c2 = [
      edge[2],
      edge[1]
    ];



    return `M ${edge[0]} ${edge[1]} C ${c1[0]} ${c1[1]}, ${c2[0]} ${c2[1]}, ${edge[2]} ${edge[3]}`;
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
    // no move on input/output parameter
    if (!(<HTMLElement>event.target).classList.contains('nomove')) {
      this.movement = { index, x: event.offsetX, y: event.offsetY };
    } else {
      this.movement.index = undefined;
    }
  }

  @HostListener('mousemove', ['$event'])
  public dragMove(event: MouseEvent) {
    // return if no task / parameter is selected
    if (this.movement.index === undefined && this.movement.edge === undefined) {
      return;
    }

    // get movement data
    const n: HTMLElement = this.el.nativeElement;
    const { index, x, y } = this.movement;
    const r = n.getBoundingClientRect();

    if (this.movement.edge === undefined) {
      // Task movement

      // calcualte new position
      this.workflow.tasks[index].x = event.pageX + n.scrollLeft - r.left - x;
      this.workflow.tasks[index].y = event.pageY + n.scrollTop - r.top - y - 20;
    } else {
      // Parameter line drawing
      this.movement.edge[0] = n.scrollLeft - r.left + x;
      this.movement.edge[1] = n.scrollTop - r.top + y;
      this.movement.edge[2] = event.pageX + n.scrollLeft - r.left;
      this.movement.edge[3] = event.pageY + n.scrollTop - r.top;
    }
  }

  @HostListener('mouseup')
  public dragEnd(event) {
    // reset movement data
    this.movement = {};
    // reset cursor
    document.body.style.cursor = 'default';
  }

  public dragOver(event: DragEvent): boolean {
    // this needs to return false validate dropping area
    return false;
  }

  public drop(event: DragEvent) {
    // get process data from drag and drop event
    try {
      const process: Process = JSON.parse(event.dataTransfer.getData('json'));
      this.add(process, event.offsetX - 100, event.offsetY - 50);
    } catch (e) { }
  }

  public parameterDrag(parameter: ProcessParameter<'input' | 'output'>, task: TaskComponent) {
    const [x, y] = task.getParameterPosition(parameter.role, parameter.id);
    this.movement = {
      edge: [0, 0, 0, 0],
      x, y
    };
    // Set cursor
    document.body.style.cursor = 'pointer';
  }
}
