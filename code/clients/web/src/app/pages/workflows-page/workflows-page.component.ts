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

  /**
   * creates the workflow page object
   * @param processService fetches process data
   * @param workflowService fetches workflow data
   * @param router enables routing
   */
  constructor(
    private processService: ProcessService,
    private workflowService: WorkflowService,
    private router: Router,
  ) {

  }

  /**
   * is called after an appropriate time to get
   * all workflows and processes
   */
  public ngOnInit() {
    this.workflowService.all().subscribe(workflows => this.workflows = workflows);
    this.processService.all().subscribe(processes => this.processes = processes);
  }

  /**
   * checks wether a workflow is opened
   * @param workflow the workflow which is checked
   */
  public opened(workflow: Workflow) {
    this.openedWorkflowID = workflow.id;
  }

  /**
   * checks wether a workflow is closed
   * @param workflow the workflow which is checked
   */
  public closed(workflow: Workflow) {
    if (this.openedWorkflowID === workflow.id) {
      this.openedWorkflowID = -1;
    }
  }

  /**
   * removes a workflow
   * @param id the id of the workflow which is removed
   */
  public remove(id: number) {
    const index = this.workflows.findIndex(workflow => workflow.id === id);
    if (index !== -1) {
      this.workflows.splice(index, 1);
      this.workflowService.remove(id);
    }
  }

  /**
   * routes to the editor opening a workflow
   * @param id the id of the workflow which is opened
   */
  public edit(id: number) {
    this.router.navigate([`/editor/${id}`]);
  }

  /**
   * gets a workflow from the database
   * @param id the id of the workflow which is returned
   */
  public getWorkflow(id: number): Observable<Workflow> {
    return this.workflowService.get(id);
  }

  /**
   * executes a workflow
   * @param id the id of the workflow which is executed
   */
  public run(id: number) {
    this.workflowService.start(id);
  }

  /**
   * validates a workflow
   * @param workflow the id of the workflow which is validated
   */
  public validate(workflow): boolean {
    return this.workflowService.validate(workflow) === WorkflowValidationResult.SUCCESSFUL;
  }

  /**
   * checks if a workflow is running
   * @param worflow the workflow which is checked
   */
  public runs(worflow: Workflow): boolean {
    return this.workflowService.isRunning(worflow);
  }
}
