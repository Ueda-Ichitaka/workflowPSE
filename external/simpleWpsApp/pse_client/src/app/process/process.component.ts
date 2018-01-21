import { Component, OnInit, ViewEncapsulation, ViewChild, Input, HostListener, HostBinding, EventEmitter, ElementRef, Output } from '@angular/core';

@Component({
  selector: 'app-process',
  templateUrl: './process.component.html',
  styleUrls: ['./process.component.scss'],
  encapsulation: ViewEncapsulation.None
})
export class ProcessComponent implements OnInit {

  @Input()
  data: any = {};

  @Input()
  @HostBinding('class.movable')
  movable = false;

  @Output()
  clickOutput = new EventEmitter<string>();

  @Output()
  clickInput = new EventEmitter<string>();

  @ViewChild('outputs')
  outputParentComponents: ElementRef;

  @ViewChild('inputs')
  inputParentComponents: ElementRef;

  isMoving = false;


  constructor(private el: ElementRef) { }

  public getInputRect(name: string) {
    const index = (<any>this.data).input.indexOf(name);
    const native: HTMLElement = this.inputParentComponents.nativeElement;
    const box = native.children.item(index).getBoundingClientRect();
    return box;
  }

  public getOutputRect(name: string) {
    const index = (<any>this.data).output.indexOf(name);
    const native: HTMLElement = this.outputParentComponents.nativeElement;
    const box = native.children.item(index).getBoundingClientRect();
    return box;
  }

  @HostListener('window:mousemove', ['$event'])
  mouseMove(event: MouseEvent) {
    if (!this.isMoving) {
      return;
    }

    const native: HTMLElement = this.el.nativeElement;
    const box = native.parentElement.getBoundingClientRect();
    const x = event.pageX - box.left - 50;
    const y = event.pageY - box.top - 25;

    native.style.left = x + 'px';
    native.style.top = y + 'px';
  }

  @HostListener('mouseup')
  mouseUp() {
    this.isMoving = false;
  }

  @HostListener('mousedown', ['$event.target'])
  mouseDown(target: HTMLDivElement) {
    if (target.classList.contains('output') || target.classList.contains('input')) {
      return;
    }
    this.isMoving = true;
  }

  ngOnInit() {
  }


}
