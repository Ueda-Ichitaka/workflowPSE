import { Component, OnInit } from '@angular/core';
import { WorkflowService } from 'app/services/workflow.service';
import { Workflow } from 'app/models/Workflow';
import { Observable } from 'rxjs/Observable';
import { Router } from '@angular/router';

@Component({
  selector: 'app-workflows-page',
  templateUrl: './workflows-page.component.html',
  styleUrls: ['./workflows-page.component.scss']
})
export class WorkflowsPageComponent implements OnInit {

  public workflows: Observable<Workflow[]>;

  constructor(private workflowService: WorkflowService, private router: Router) {
    this.workflows = this.workflowService.all();
  }

  public ngOnInit() {
  }

  public edit(id: number) {
    this.router.navigate(['/editor', { id }]);
  }
}
