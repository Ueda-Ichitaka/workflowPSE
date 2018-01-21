import { Component, OnInit } from '@angular/core';
import { WorkflowService, WorkflowValidationResult } from 'app/services/workflow.service';
import { Workflow } from 'app/models/Workflow';
import { Observable } from 'rxjs/Observable';
import { Router } from '@angular/router';
import { ProcessService } from 'app/services/process.service';
import { Process } from 'app/models/Process';

@Component({
  selector: 'app-workflows-page',
  templateUrl: './workflows-page.component.html',
  styleUrls: ['./workflows-page.component.scss']
})
export class WorkflowsPageComponent implements OnInit {

  public workflows: Workflow[];
  public processes: Process[];

  public openedWorkflowID = -1;

  constructor(
    private processService: ProcessService,
    private workflowService: WorkflowService,
    private router: Router,
  ) {

  }

  public ngOnInit() {
    this.workflowService.all().subscribe(workflows => this.workflows = workflows);
    this.processService.all().subscribe(processes => this.processes = processes);
  }

  public opened(workflow: Workflow) {
    this.openedWorkflowID = workflow.id;
  }

  public closed(workflow: Workflow) {
    if (this.openedWorkflowID === workflow.id) {
      this.openedWorkflowID = -1;
    }
  }

  public remove(id: number) {
    const index = this.workflows.findIndex(workflow => workflow.id === id);
    if (index !== -1) {
      this.workflows.splice(index, 1);
      this.workflowService.remove(id);
    }
  }

  public edit(id: number) {
    this.router.navigate(['/editor', { id }]);
  }

  public getWorkflow(id: number): Observable<Workflow> {
    return this.workflowService.get(id);
  }

  public run(id: number) {
    this.workflowService.execute(id);
  }

  public validate(workflow): boolean {
    return this.workflowService.validate(workflow) === WorkflowValidationResult.SUCCESSFUL;
  }

  public runs(worflow: Workflow): boolean {
    return this.workflowService.isRunning(worflow);
  }
}
