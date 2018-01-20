import {
  Component, OnInit, HostListener, ElementRef, Input, QueryList,
  ViewChildren, NgZone, ChangeDetectionStrategy, EventEmitter, Output,
  ChangeDetectorRef
} from '@angular/core';
import { Process } from 'app/models/Process';
import { Edge } from 'app/models/Edge';
import { ViewChild } from '@angular/core';
import { Workflow } from 'app/models/Workflow';
import { Task, TaskState } from 'app/models/Task';
import { ProcessParameter } from 'app/models/ProcessParameter';
import { MediaQueryListListener } from '@angular/flex-layout';
import { TaskComponent } from 'app/components/task/task.component';

interface MovementData {
  parameter?: ProcessParameter<'input' | 'output'>;
  edge?: [number, number, number, number];
  task?: Task;
  index?: number;
  x?: number;
  y?: number;
  before?: string;
}

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  styleUrls: ['./editor.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush
})
export class EditorComponent implements OnInit {

  @Input()
  public workflow: Workflow;

  @Input()
  public processes: Process[];

  private movement: MovementData = {};

  private snapshots: Workflow[] = [];

  @ViewChildren(TaskComponent)
  private taskComponents: QueryList<TaskComponent>;

  @Output()
  public workflowChanged = new EventEmitter<Workflow>();

  public constructor(private el: ElementRef, private zone: NgZone, private cd: ChangeDetectorRef) {

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

    setTimeout(() => {
      this.cd.detectChanges();
      this.workflowChanged.emit(this.workflow);
    }, 100);
  }

  public getSvgEdge(edge: [number, number, number, number], mouse = false) {
    let delta = Math.abs(edge[1] - edge[3]);
    if (mouse === true && this.movement.parameter !== undefined) {
      delta *= this.movement.parameter.role === 'input' ? -1 : 1;
    }

    return `M ${edge[0]} ${edge[1]} C ${edge[0]} ${edge[1] + delta}, ${edge[2]} ${edge[3] - delta}, ${edge[2]} ${edge[3]}`;
  }

  public get edges(): [number, number, number, number][] {
    if (this.taskComponents === undefined) {
      return;
    }

    const out = [];
    const n: HTMLElement = this.el.nativeElement;
    const r = n.getBoundingClientRect();

    for (const edge of this.workflow.edges) {
      const aComponent = this.taskComponents
        .find(component => component.task.id === edge.a_id);

      const bComponent = this.taskComponents
        .find(component => component.task.id === edge.b_id);

      if (!aComponent || !bComponent) {
        return;
      }

      const a = aComponent.getParameterPosition('output', edge.output_id);
      const b = bComponent.getParameterPosition('input', edge.input_id);

      if (a === null || b === null) {
        return;
      }

      out.push([
        a[0] - r.left + n.scrollLeft,
        a[1] - r.top + n.scrollTop,
        b[0] - r.left + n.scrollLeft,
        b[1] - r.top + n.scrollTop,
      ]);
    }
    return out;
  }

  public add(process: Process, x: number, y: number) {
    this.snapshot();
    const timestamp = (new Date()).getTime();

    // create task
    const task: Task = {
      id: Math.round(Math.random() * 10000),
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
    this.cd.detectChanges();
    this.workflowChanged.emit(this.workflow);
  }

  public remove(task_id: number) {
    this.snapshot();
    const index = this.workflow.tasks.findIndex(task => task.id === task_id);
    this.workflow.tasks.splice(index, 1);
    this.workflow.edges = this.workflow.edges.filter(edge => edge.a_id !== task_id && edge.b_id !== task_id);

    this.cd.detectChanges();
    this.workflowChanged.emit(this.workflow);
  }

  public findProcess(id: number): Process {
    return this.processes.find(process => process.id === id);
  }

  public dragStart(index: number, event: MouseEvent) {
    // store index of moved task
    // no move on input/output parameter
    if (!(<HTMLElement>event.target).classList.contains('nomove')) {
      let x = event.offsetX;
      let y = event.offsetY;
      if ((<HTMLElement>event.target).localName !== 'app-task') {
        x += 16;
        y += 16;
      }
      this.movement = { index, x, y, before: JSON.stringify(this.workflow) };
    } else {
      this.movement.index = undefined;
    }
  }

  @HostListener('mousemove', ['$event'])
  public dragMove(event: MouseEvent) {
    // return if no task / parameter is selected
    if (this.movement.index === undefined && this.movement.edge === undefined) {
      return true;
    }

    // get movement data
    const n: HTMLElement = this.el.nativeElement;
    const r = n.getBoundingClientRect();
    const { index, x, y } = this.movement;

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

    if (this.movement.before !== undefined) {
      this.snapshot(JSON.parse(this.movement.before));
    }

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
      task: task.task,
      parameter,
      x, y
    };

    // Set cursor
    document.body.style.cursor = 'pointer';
  }

  public parameterDrop(parameter: ProcessParameter<'input' | 'output'>, task: TaskComponent) {
    if (!this.movement.parameter || parameter.role === this.movement.parameter.role) {
      return;
    }

    if (this.movement.edge) {
      this.snapshot();
      const input_id = parameter.role === 'input' ? parameter.id : this.movement.parameter.id;
      const output_id = parameter.role === 'output' ? parameter.id : this.movement.parameter.id;
      const a_id = parameter.role === 'output' ? task.task.id : this.movement.task.id;
      const b_id = parameter.role === 'input' ? task.task.id : this.movement.task.id;

      this.workflow.edges.push({ id: -1, a_id, b_id, input_id, output_id });
    }
  }

  private snapshot(workflow?: Workflow) {
    if (workflow) {
      this.snapshots.push(workflow);
    } else {
      this.snapshots.push(JSON.parse(JSON.stringify(this.workflow)));
    }
  }

  public undo() {
    const snapshot = this.snapshots.pop();
    if (snapshot !== undefined) {
      this.workflow = snapshot;
    }
    this.cd.detectChanges();
    this.workflowChanged.emit(this.workflow);
  }

  public canUndo(): boolean {
    return this.snapshots.length > 0;
  }
}
