import { Component, OnInit, ElementRef, ViewEncapsulation, HostListener, QueryList, ViewChild, ViewChildren, Input } from '@angular/core';
import { ProcessComponent } from '../process/process.component';
import { Observable } from 'rxjs/Observable';

@Component({
  selector: 'app-editor',
  templateUrl: './editor.component.html',
  styleUrls: ['./editor.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class EditorComponent implements OnInit {

  @Input()
  processes: Observable<any[]>;

  drawnProcesses = [];
  drawnLines = [];
  connections = [

  ];

  newConnect = {};
  isDown = false;

  @ViewChildren(ProcessComponent)
  processComponents: QueryList<ProcessComponent>;

  constructor(public el: ElementRef) { }

  public add(p) {
    this.drawnProcesses.push(p);
  }

  clickProcessInput(name: string, p: ProcessComponent) {
    const index = this.processComponents.toArray().indexOf(p);

    this.newConnect['in'] = [index, name];
    if (this.newConnect['in'] !== undefined && this.newConnect['out'] !== undefined) {
      this.connections.push(<any>this.newConnect);
      this.newConnect = {};
      this.updateLines();
    }
  }

  clickProcessOutput(name: string, p: ProcessComponent) {
    const index = this.processComponents.toArray().indexOf(p);

    this.newConnect['out'] = [index, name];
    if (this.newConnect['in'] !== undefined && this.newConnect['out'] !== undefined) {
      this.connections.push(<any>this.newConnect);
      this.newConnect = {};
      this.updateLines();
    }
  }

  public updateLines() {
    this.drawnLines = [];
    if (!this.processComponents) {
      return;
    }
    const components = this.processComponents.toArray();
    const box: ClientRect = this.el.nativeElement.getBoundingClientRect();
    for (const c of this.connections) {
      if (c.out[0] >= components.length || c.in[0] >= components.length) {
        continue;
      }

      const box0 = components[c.out[0]].getOutputRect(c.out[1]);
      const box1 = components[c.in[0]].getInputRect(c.in[1]);

      if (!box0 || !box1) {
        continue;
      }

      this.drawnLines.push({
        x1: box0.left - box.left + 8,
        y1: box0.top - box.top + 8,
        x2: box1.left - box.left + 8,
        y2: box1.top - box.top + 8
      });
    }
  }

  ngOnInit() {
  }

  @HostListener('mousemove', ['$event'])
  public mousemove(event: MouseEvent) {
    if (this.isDown) {
      this.updateLines();
    }

  }

  @HostListener('mousedown', ['$event'])
  public mousedown(event: MouseEvent) {
    this.isDown = true;
  }

  @HostListener('mouseup', ['$event'])
  public mouseup(event: MouseEvent) {
    this.isDown = false;
  }

}
