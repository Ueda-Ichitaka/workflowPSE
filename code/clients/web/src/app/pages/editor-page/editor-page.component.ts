import { Component, OnInit, Input, ViewChild, ElementRef, ChangeDetectionStrategy, ChangeDetectorRef, NgZone } from '@angular/core';
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
import { MatDialog } from '@angular/material';
import { ResultDialogComponent } from 'app/components/result-dialog/result-dialog.component';
import { take } from 'rxjs/operators';

/**
 * Editor page.
 *
 * @export
 * @class EditorPageComponent
 * @implements {OnInit}
 */
@Component({
  selector: 'app-editor-page',
  templateUrl: './editor-page.component.html',
  styleUrls: ['./editor-page.component.scss'],
  changeDetection: ChangeDetectionStrategy.OnPush,
  animations: [
    trigger('slide', [
      transition(':enter', [
        style({ transform: 'translateX(100%)' }),
        animate('233ms ease-in-out')
      ]),
      transition(':leave', [
        animate('233ms ease-in-out', style({ transform: 'translateX(100%)' }))
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

  private canRefreshWorkflow = true;

  /**
   * Creates an instance of EditorPageComponent.
   *
   * @param {ProcessService} processService
   * @param {WorkflowService} workflowService
   * @param {WpsService} wpsService
   * @param {ActivatedRoute} route
   * @param {Router} router
   * @param {MatDialog} dialog
   * @param {ChangeDetectorRef} cd
   * @param {NgZone} zone
   * @memberof EditorPageComponent
   */
  constructor(
    private processService: ProcessService,
    private workflowService: WorkflowService,
    private wpsService: WpsService,
    private route: ActivatedRoute,
    private router: Router,
    public dialog: MatDialog,
    private cd: ChangeDetectorRef,
    private zone: NgZone,
  ) {

  }

  /**
   * Sets up this component.
   *
   * @memberof EditorPageComponent
   */
  ngOnInit() {
    this.processes = this.processService.all();
    this.wps = this.wpsService.all();

    this.route.params.subscribe(params => {
      if (params['id'] !== undefined) {
        this.fresh = false;
        this.workflowService.get(+params['id']).subscribe(w => {
          this.workflow = w;
        });
      } else {
        this.fresh = true;
        this.workflow = {
          id: -Math.round(Math.random() * 10000),
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


    setInterval(() => {
      this.updateWorkflowStatus();
    }, 1500);


    setTimeout(() => {
      this.workflowChanged(this.workflow);
      this.cd.detectChanges();
    }, 500);
  }

  /**
   * Shows result dialog.
   *
   * @memberof EditorPageComponent
   */
  public showResults() {
    this.dialog.open(ResultDialogComponent, {
      data: this.workflow
    });
  }

  /**
   * Updates workflow status.
   *
   * @returns {Promise<void>} Updated
   * @memberof EditorPageComponent
   */
  public async updateWorkflowStatus(): Promise<void> {
    if (!this.canRefreshWorkflow || !this.runs()) { return; }
    this.canRefreshWorkflow = false;
    this.workflow = await this.workflowService.get(this.workflow.id).toPromise();
    await this.workflowService.refresh(this.workflow.id);
    console.log('-- Refreshed Workflow Execution Status --');
    this.canRefreshWorkflow = true;
    setTimeout(() => { this.cd.detectChanges(); }, 1);
  }

  /**
   * Toggles whether the process list
   * is shown
   *
   * @memberof EditorPageComponent
   */
  public toggleProcessList() {
    this.showProcessList = !this.showProcessList;
  }

  /**
   * Reverts the last workflow.
   *
   * @memberof EditorPageComponent
   */
  public undo() {
    this.editorComponent.undo();
  }

  /**
   * Tells whether there is something to undo.
   *
   * @returns {boolean} Can Undo
   * @memberof EditorPageComponent
   */
  public canUndo(): boolean {
    return this.editorComponent ? this.editorComponent.canUndo() : false;
  }

  /**
   * Executes workflow if not empty.
   *
   * @param id the id of the workflow
   */
  public async run() {
    if (!this.workflow) {
      return;
    }

    await this.save();

    await this.workflowService.start(this.workflow.id);
    this.workflowService.get(this.workflow.id).pipe(take(1)).subscribe(workflow => {
      this.workflow = workflow;
      setTimeout(() => { this.cd.detectChanges(); }, 10);
    });
    this.updateWorkflowStatus();
  }

  /**
   * Stops running workflow.
   *
   * @memberof EditorPageComponent
   */
  public async stop() {
    await this.workflowService.stop(this.workflow.id);
    this.workflowService.get(this.workflow.id).pipe(take(1)).subscribe(workflow => {
      this.workflow = workflow;
      setTimeout(() => { this.cd.detectChanges(); }, 10);
    });
    this.updateWorkflowStatus();
  }

  /**
   * Changes the name of the workflow.
   *
   * @param name new name of the workflow
   */
  public editTitle(name: string) {
    if (name.length === 0) {
      name = 'My Workflow';
    } else if (name.length > 24) {
      name = name.slice(0, 24);
    }


    this.workflow.title = name;

    if (this.fresh) {
      this.workflowService.create(this.editorComponent.workflow).subscribe(obj => {
        this.router.navigate([`/editor/${obj.id}`]);
      });
    } else {
      this.workflowService.update(this.workflow.id, this.workflow).toPromise();
    }

    this.workflowChanged(this.workflow);
    this.editTitleMode = false;
  }

  /**
   * Enables clicking the title in order to change it.
   *
   * @memberof EditorPageComponent
   */
  public clickTitleEdit() {
    this.editTitleMode = true;
    setTimeout(() => {
      const native: HTMLInputElement = this.titleInputComponent.nativeElement;
      native.focus();
    }, 150);
  }

  /**
   * Saves the workflow.
   *
   * @returns {Promise<Workflow>} Saved workflow
   * @memberof EditorPageComponent
   */
  public async save(): Promise<Workflow> {
    if (this.fresh) {
      this.workflowService.create(this.editorComponent.workflow).subscribe(obj => {
        this.router.navigate([`/editor/${obj.id}`]);
      });
    } else {
      const result = await this.workflowService.update(this.workflow.id, this.workflow).toPromise();
      setTimeout(() => { this.cd.detectChanges(); }, 10);
      return result;
    }
  }


  /**
   * Tells whether the current workflow is running.
   *
   * @returns {boolean} Is Running
   * @memberof EditorPageComponent
   */
  public runs(): boolean {
    if (!this.workflow) {
      return null;
    }
    const running = this.workflowService.isRunning(this.workflow);
    this.canRefreshWorkflow = running && !this.finished();
    return running;
  }

  /**
   * Tells whether the current workflow is finished.
   *
   * @returns {boolean} Is Finished
   * @memberof EditorPageComponent
   */
  public finished(): boolean {
    return this.workflowService.finished(this.workflow);
  }

  /**
   * Tells if the workflow has changed.
   *
   * @param workflow the workflow which is checked
   */
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
      { type: WorkflowValidationResult.MULIPLE_INPUTS, message: 'Workflow has taks with multiple inputs' },
    ];

    const result = errorMessages.find(m => m.type === this.workflowService.validate(workflow));
    this.workflowError = result ? result.message : 'No Error Message Found';
  }

}
