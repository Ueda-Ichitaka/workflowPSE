import { Component, OnInit } from '@angular/core';
import { WorkflowService } from 'app/services/workflow.service';
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

  public edit(id: number) {
    this.router.navigate(['/editor', { id }]);
  }

  public getWorkflow(id: number): Observable<Workflow> {
    return this.workflowService.get(id);
  }
}
