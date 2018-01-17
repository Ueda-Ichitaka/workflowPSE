import { Component, OnInit, Input, ViewChild } from '@angular/core';
import { ProcessService } from 'app/services/process.service';
import { Observable } from 'rxjs/Observable';
import { Process } from 'app/models/Process';
import { ActivatedRoute } from '@angular/router';
import { Workflow } from 'app/models/Workflow';
import { WorkflowService } from 'app/services/workflow.service';

@Component({
  selector: 'app-editor-page',
  templateUrl: './editor-page.component.html',
  styleUrls: ['./editor-page.component.scss']
})
export class EditorPageComponent implements OnInit {

  public workflow: Observable<Workflow>;
  public processes: Observable<Process[]>;

  @ViewChild('sidenav')
  public sidenavComponent;

  @Input()
  public showProcessList = true;


  constructor(
    private processService: ProcessService,
    private workflowService: WorkflowService,
    private route: ActivatedRoute
  ) {

  }

  ngOnInit() {
    this.processes = this.processService.all();
    this.route.params.subscribe(params => {
      if (params['id'] !== undefined) {
        this.workflow = this.workflowService.get(+params['id']);
      }
    });
  }

  public toggleProcessList() {
    this.showProcessList = !this.showProcessList;
  }

  public openSettings() {
    this.sidenavComponent.toggle();
  }

}
