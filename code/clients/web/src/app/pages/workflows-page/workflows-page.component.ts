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

  public workflows: Observable<Workflow[]>;
  public processes: Observable<Process[]>;

  constructor(
    private processService: ProcessService,
    private workflowService: WorkflowService,
    private router: Router,
  ) {
    this.processes = this.processService.all();
    this.workflows = this.workflowService.all();
  }

  public ngOnInit() {
  }

  public remove(id: number) {
    this.workflowService.remove(id);
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
