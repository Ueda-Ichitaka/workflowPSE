import { Component, OnInit, HostListener, ElementRef, Input } from '@angular/core';
import { Process } from 'app/models/Process';
import { ViewChild } from '@angular/core';
import { Workflow } from 'app/models/Workflow';

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  styleUrls: ['./editor.component.scss']
})
export class EditorComponent implements OnInit {

  public drawnProcesses: {
    process: Process,
    x: number,
    y: number
  }[] = [];

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

  private movingProcessIndex: number;
  private movingOffX: number;
  private movingOffY: number;

  @Input()
  public workflow: Workflow;

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

  public dragOver(event: DragEvent): boolean {
    return false;
  }

  public drop(event: DragEvent) {
    const process: Process = JSON.parse(event.dataTransfer.getData('json'));
    this.add(process, event.offsetX - 100, event.offsetY - 50);
  }


  public add(process: Process, x: number, y: number) {
    this.drawnProcesses.push({ process, x, y });
  }

  public dragStart(index: number, event: MouseEvent) {
    this.movingProcessIndex = index;
    this.movingOffY = event.offsetY;
    this.movingOffX = event.offsetX;
  }

  @HostListener('mousemove', ['$event'])
  public dragMove(event: MouseEvent) {
    if (this.movingProcessIndex === undefined) {
      return;
    }

    const n: HTMLElement = this.el.nativeElement;
    const r = n.getBoundingClientRect();

    this.drawnProcesses[this.movingProcessIndex].x = event.pageX + n.scrollLeft - r.left - this.movingOffX;
    this.drawnProcesses[this.movingProcessIndex].y = event.pageY + n.scrollTop - r.top - this.movingOffY - 20;
  }

  @HostListener('mouseup')
  public dragEnd(event) {
    this.movingProcessIndex = undefined;
  }



}
