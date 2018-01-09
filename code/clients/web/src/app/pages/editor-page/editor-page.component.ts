import { Component, OnInit, Input } from '@angular/core';

@Component({
  selector: 'app-editor-page',
  templateUrl: './editor-page.component.html',
  styleUrls: ['./editor-page.component.scss']
})
export class EditorPageComponent implements OnInit {

  constructor() { }

  @Input()
  public showProcessList = true;

  ngOnInit() {
  }

  public toggleProcessList() {
    this.showProcessList = !this.showProcessList;
  }

}
