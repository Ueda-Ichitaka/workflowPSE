import {Injectable} from '@angular/core';
import {Workflow} from '../models/Workflow';
import {Edge} from '../models/Edge';
import {TaskState} from '../models/Task';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs/Observable';
import {map, switchMap} from 'rxjs/operators';
import {MatSnackBar} from '@angular/material';
import {Process} from 'app/models/Process';
import {ProcessService} from 'app/services/process.service';

export enum WorkflowValidationResult {
  ERROR,
  SUCCESSFUL,
  TITLE_TOO_LONG,
  TITLE_TOO_SHORT,
  EMPTY,
  LOOP_TO_SAME_TASK,
  WRONG_INPUT_TYPES,
  MISSING_TASK_INPUT,
  MISSING_WORKFLOW,
  MISSING_PROCESSES,
  CYCLE_IN_WORKFLOW,
}

@Injectable()
export class WorkflowService {
  private processes?: Process[];

  constructor(private http: HttpClient, private bar: MatSnackBar, private processService: ProcessService) {
    this.processService.all().subscribe(processes => this.processes = processes);
  }

  private getKeyFromId(id: number): Observable<string> {
    return this.http.get<{ [key: string]: Workflow }>(`https://wpsflow.firebaseio.com/workflow.json`).pipe(
      map(obj => Object.entries(obj).find(([key, workflow]) => workflow.id === id)),
      map(([key, workflow]) => key),
    );
  }

  public all(): Observable<Workflow[]> {
    return this.http.get<{ [key: string]: Workflow }>(`https://wpsflow.firebaseio.com/workflow.json`).pipe(
      map(obj => Object.values(obj)),
      map(obj => obj.map(workflow => {
        workflow.edges = workflow.edges || [];
        workflow.tasks = workflow.tasks || [];
        return workflow;
      }))
    );
  }

  public get(id: number): Observable<Workflow> {
    return this.getKeyFromId(id).pipe(
      switchMap(key => this.http.get<Workflow>(`https://wpsflow.firebaseio.com/workflow/${key}.json`))
    );
  }

  public create(workflow: Partial<Workflow>): Observable<Workflow> {
    this.bar.open(`Created Workflow`, 'CLOSE', {duration: 3000});
    return this.http.post<Workflow>(`https://wpsflow.firebaseio.com/workflow.json`, workflow).pipe(
      map(obj => <Workflow>workflow)
    );
  }

  public update(id: number, workflow: Partial<Workflow>): Observable<Workflow> {
    this.bar.open(`Saved Workflow`, 'CLOSE', {duration: 3000});
    return this.getKeyFromId(id).pipe(
      switchMap(key => this.http.put<Workflow>(`https://wpsflow.firebaseio.com/workflow/${key}.json`, workflow))
    );
  }

  public async remove(id: number): Promise<boolean> {
    this.bar.open(`Deleted Workflow`, 'CLOSE', {duration: 3000});
    return this.getKeyFromId(id).pipe(
      switchMap(key => this.http.delete<boolean>(`https://wpsflow.firebaseio.com/workflow/${key}.json`))
    ).toPromise();

  }

  public isRunning(workflow: Partial<Workflow>): boolean {
    if (!workflow.tasks) {
      return false;
    }
    const index = workflow.tasks
      .findIndex(task => task.state === TaskState.WAITING || task.state === TaskState.FAILED);
    return index !== -1;
  }

  // TODO: @David Validate workflow
  public validate(workflow: Workflow): WorkflowValidationResult {
    if (!workflow) {
      return WorkflowValidationResult.MISSING_WORKFLOW;
    } else if (!this.processes) {
      return WorkflowValidationResult.MISSING_PROCESSES;
    }

    // check name
    if (workflow.title.length > 255) {
      return WorkflowValidationResult.TITLE_TOO_LONG;
    } else if (workflow.title.length < 1) {
      return WorkflowValidationResult.TITLE_TOO_SHORT;
    } else if (workflow.tasks && workflow.tasks.length < 1) {
      return WorkflowValidationResult.EMPTY;
    } else if (workflow.edges) {
      for (let i = 0; i < workflow.edges.length; i++) {
        // check for loop to same task
        if (workflow.edges[i].a_id === workflow.edges[i].b_id) {
          return WorkflowValidationResult.LOOP_TO_SAME_TASK;
        }
        // check for wrong input types
        let inputTaskNumber: number = null;
        let outputTaskNumber: number = null;
        for (let j = 0; j < workflow.tasks.length; j++) {
          if (workflow.tasks[j].id === workflow.edges[i].b_id) {
            inputTaskNumber = workflow.tasks[j].process_id;
          }
          if (workflow.tasks[j].id === workflow.edges[i].a_id) {
            outputTaskNumber = workflow.tasks[j].process_id;
          }
        }
        let inputProcessNumber: number = null;
        let outputPrecessNumber: number = null;
        for (let k = 0; k < this.processes.length; k++) {
          if (this.processes[k].id === inputTaskNumber) {
            inputProcessNumber = k;
          }
          if (this.processes[k].id === outputTaskNumber) {
            outputPrecessNumber = k;
          }
        }
        let processParameterTypeCorrect = false;
        for (let l = 0; l < this.processes[inputProcessNumber].inputs.length; l++) {
          for (let m = 0; m < this.processes[outputPrecessNumber].outputs.length; m++) {
            if (this.processes[inputProcessNumber].inputs[l].type === this.processes[outputPrecessNumber].outputs[m].type) {
              processParameterTypeCorrect = true;
            }
          }
        }
        if (!processParameterTypeCorrect) {
          return WorkflowValidationResult.WRONG_INPUT_TYPES;
        }
      }

    }
    // check for missing input
    if (workflow.tasks && workflow.edges) {
      for (let i = 0; i < workflow.tasks.length; i++) {
        let numberOfInputs = 0;
        for (let k = 0; k < workflow.edges.length; k++) {
          if (workflow.edges[k].b_id === workflow.tasks[i].id) {
            numberOfInputs++;
          }
        }
        for (let j = 0; j < this.processes.length; j++) {
          if (workflow.tasks[i].process_id === this.processes[j].id) {
            if (numberOfInputs < this.processes[j].inputs.length) {
              return WorkflowValidationResult.MISSING_TASK_INPUT;
            }
          }
        }
      }
    }

    // - cycle check
    if (workflow.tasks && workflow.edges) {
      let checkedTasks: number[] = [];
      for (let i = 0; i < workflow.edges.length; i++) {
        let visitedTasks: number[] = [];
        if (!this.contains(checkedTasks, workflow.edges[i].a_id)) {
          if (this.checkCycle(workflow.edges[i], workflow, visitedTasks)) {
            return WorkflowValidationResult.CYCLE_IN_WORKFLOW;
          }
          checkedTasks = visitedTasks;
        }
      }
    }

    // TODO: @David add additional checks

    return WorkflowValidationResult.SUCCESSFUL;
  }

  private contains<T>(array: Array<T>, variable: T): boolean {
    for (let i = 0; i < array.length; i++) {
      if (array[i] === variable) {
        return true;
      }
    }
    return false;
  }

  private checkCycle(currentWorkflowEdge: Edge, workflow: Partial<Workflow>, visitedTasks: number[]): boolean {
     visitedTasks.push(currentWorkflowEdge.a_id);
    // check task at end of edge
    for (let i = 0; i < workflow.tasks.length; i++) {
      if (this.contains(visitedTasks, currentWorkflowEdge.b_id)) {
        return true;
      }
      if (workflow.tasks[i].id === currentWorkflowEdge.b_id) {
        // check for new edges at task
        let cycle = false;
        for (let j = 0; j < workflow.edges.length; j++) {
          if (workflow.edges[j].a_id === workflow.tasks[i].id) {
            if (this.contains(visitedTasks, workflow.edges[j].b_id)) {
              return true;
            }
            cycle = cycle || this.checkCycle(workflow.edges[j], workflow, visitedTasks);
          }
        }
        return cycle;
      }
    }
    return false;
  }

  public async execute(id: number): Promise<boolean> {

    // if (w.tasks.length > 0) {
    //   w.tasks[0].state = TaskState.WAITING;
    // }


    // TODO execute workflow

    // this.bar.open(`${w.title} Executed`, 'CLOSE', { duration: 3000 });

    return true;
  }
}
