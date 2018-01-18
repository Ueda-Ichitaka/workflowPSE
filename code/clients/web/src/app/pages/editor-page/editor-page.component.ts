import { Component, OnInit, Input, ViewChild } from '@angular/core';
import { ProcessService } from 'app/services/process.service';
import { Observable } from 'rxjs/Observable';
import { Process } from 'app/models/Process';
import { ActivatedRoute } from '@angular/router';
import { Workflow } from 'app/models/Workflow';
import { WorkflowService, WorkflowValidationResult } from 'app/services/workflow.service';

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

  public workflowError = 'error';

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

  public workflowChanged(workflow: Workflow) {
    const errorMessages = [
      { type: WorkflowValidationResult.SUCCESSFUL, message: '' },
      { type: WorkflowValidationResult.ERROR, message: 'Unknown Error' },
      { type: WorkflowValidationResult.TITLE_TO_LONG, message: 'Workflow name is to long' },
      { type: WorkflowValidationResult.TITLE_TO_SHORT, message: 'Workflow name is to short' },
    ];

    this.workflowError = errorMessages
      .find(m => m.type === this.workflowService.validate(workflow))
      .message;

    console.log(this.workflowError);
  }

}
