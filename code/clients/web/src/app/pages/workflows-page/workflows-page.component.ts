import { Component, OnInit } from '@angular/core';

@Component({
  selector: 'app-workflows-page',
  templateUrl: './workflows-page.component.html',
  styleUrls: ['./workflows-page.component.scss']
})
export class WorkflowsPageComponent implements OnInit {

  workflows = [];

  constructor() {
    for (let i = 0; i < 20; i++) {
      this.workflows.push({
        id: i,
        title: 'Workflow' + i
      });
    }
  }

  ngOnInit() {
  }

}
