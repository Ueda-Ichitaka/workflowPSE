import { Component, OnInit, Input, HostListener, HostBinding, ElementRef } from '@angular/core';
import { MatDialog } from '@angular/material';
import { ProcessParameterType } from 'app/models/ProcessParameter';
import { ProcessDetailDialogComponent } from 'app/components/process-detail-dialog/process-detail-dialog.component';


@Component({
  selector: 'app-process',
  templateUrl: './process.component.html',
  styleUrls: ['./process.component.scss']
})
export class ProcessComponent implements OnInit {

  @Input()
  public process;

  @HostBinding('draggable')
  public draggable = true;

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



  @HostListener('dragstart', ['$event'])
  public dragStart(event: DragEvent) {
    const native: HTMLElement = this.el.nativeElement;

    for (let i = 0; i < native.childElementCount; i++) {
      const c = native.children[i];
      if (c.classList.contains('container')) {
        event.dataTransfer.setDragImage(c, c.clientWidth / 2, c.clientHeight / 2);
        event.dataTransfer.setData('json', JSON.stringify(this.process));
        break;
      }
    }

  }

  public ngOnInit() {

  }

}
