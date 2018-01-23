import { Component, OnInit, Input, ViewChild, ElementRef } from '@angular/core';
import { ProcessService } from 'app/services/process.service';
import { Observable } from 'rxjs/Observable';
import { Process } from 'app/models/Process';
import { ActivatedRoute, Router } from '@angular/router';
import { Workflow } from 'app/models/Workflow';
import { WorkflowService, WorkflowValidationResult } from 'app/services/workflow.service';
import { EditorComponent } from 'app/components/editor/editor.component';
import { trigger, transition, animate, style } from '@angular/animations';
import { WpsService } from 'app/services/wps.service';
import { WPS } from 'app/models/WPS';

@Component({
  selector: 'app-editor-page',
  templateUrl: './editor-page.component.html',
  styleUrls: ['./editor-page.component.scss'],
  animations: [
    trigger('slide', [
      transition(':enter', [
        style({ transform: 'translateX(200%)' }),
        animate('233ms ease-in-out')
      ]),
    ])
  ]
})
export class EditorPageComponent implements OnInit {

  public workflow: Workflow;
  public processes: Observable<Process[]>;
  public wps: Observable<WPS[]>;

  public editTitleMode = false;

  @ViewChild('sidenav')
  public sidenavComponent;

  @Input()
  public showProcessList = true;

  public workflowError = 'error';

  @ViewChild(EditorComponent)
  public editorComponent: EditorComponent;


  @ViewChild('tileInput')
  public titleInputComponent: ElementRef;

  private fresh = false;

  constructor(
    private processService: ProcessService,
    private workflowService: WorkflowService,
    private wpsService: WpsService,
    private route: ActivatedRoute,
    private router: Router,
  ) {

  }

  ngOnInit() {
    this.processes = this.processService.all();
    this.wps = this.wpsService.all();

    this.route.params.subscribe(params => {
      if (params['id'] !== undefined) {
        this.fresh = false;
        this.workflowService.get(+params['id']).subscribe(w => {
          w.edges = w.edges || [];
          w.tasks = w.tasks || [];
          this.workflow = w;
        });
      } else {
        this.fresh = true;
        this.workflow = {
          id: Math.round(Math.random() * 10000),
          title: 'My New Workflow',
          edges: [],
          tasks: [],
          creator_id: 0,
          shared: false,
          created_at: (new Date()).getTime(),
          updated_at: (new Date()).getTime(),
        };
      }
    });
  }

  public toggleProcessList() {
    this.showProcessList = !this.showProcessList;
  }

  public undo() {
    this.editorComponent.undo();
  }

  public canUndo() {
    return this.editorComponent ? this.editorComponent.canUndo() : false;
  }

  public run(id: number) {
    if (!this.workflow) {
      return;
    }

    this.workflowService.execute(this.workflow.id);
  }

  public editTitle(name: string) {
    this.workflow.title = name;

    if (this.fresh) {
      this.workflowService.create(this.editorComponent.workflow).subscribe(obj => {
        this.router.navigate(['/editor', { id: obj.id }]);
      });
    } else {
      this.workflowService.update(this.workflow.id, this.workflow).toPromise();
    }

    this.workflowChanged(this.workflow);
    this.editTitleMode = false;
  }

  public clickTitleEdit() {
    this.editTitleMode = true;
    setTimeout(() => {
      const native: HTMLInputElement = this.titleInputComponent.nativeElement;
      native.focus();
    }, 100);
  }

  public save() {
    if (this.fresh) {
      this.workflowService.create(this.editorComponent.workflow).subscribe(obj => {
        this.router.navigate(['/editor', { id: obj.id }]);
      });
    } else {
      this.workflowService.update(this.workflow.id, this.workflow).toPromise();
    }
  }

  public runs(): boolean {
    if (!this.workflow) {
      return null;
    }

    return this.workflowService.isRunning(this.workflow);
  }


  public workflowChanged(workflow: Workflow) {
    const errorMessages = [
      { type: WorkflowValidationResult.SUCCESSFUL, message: '' },
      { type: WorkflowValidationResult.ERROR, message: 'Unknown Error' },
      { type: WorkflowValidationResult.TITLE_TOO_LONG, message: 'Workflow name is to long' },
      { type: WorkflowValidationResult.TITLE_TOO_SHORT, message: 'Workflow name is to short' },
      { type: WorkflowValidationResult.EMPTY, message: 'Workflow is empty' },
      { type: WorkflowValidationResult.LOOP_TO_SAME_TASK, message: 'Loop to same task' },
      { type: WorkflowValidationResult.WRONG_INPUT_TYPES, message: 'Wrong input types' },
      { type: WorkflowValidationResult.MISSING_TASK_INPUT, message: 'Missing task input' },
      { type: WorkflowValidationResult.MISSING_WORKFLOW, message: 'No Workflow provided' },
      { type: WorkflowValidationResult.MISSING_PROCESSES, message: 'No Process List provided' },
      { type: WorkflowValidationResult.CYCLE_IN_WORKFLOW, message: 'Workflow has a cycle' },
    ];

    const result = errorMessages.find(m => m.type === this.workflowService.validate(workflow));
    this.workflowError = result ? result.message : 'No Error Message Found';
  }

}
