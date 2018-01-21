import { Injectable } from '@angular/core';
import { Workflow } from '../models/Workflow';
import { Edge } from '../models/Edge';
import { Task, TaskState } from '../models/Task';
import { Artefact } from '../models/Artefact';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { map, filter, find, switchMap } from 'rxjs/operators';
import { Subscriber } from 'rxjs/Subscriber';
import { MatSnackBar } from '@angular/material';

export enum WorkflowValidationResult {
  ERROR,
  SUCCESSFUL,
  TITLE_TO_LONG,
  TITLE_TO_SHORT,
  EMPTY,
  LOOP_TO_SAME_TASK,
  WRONG_INPUT_TYPES,
  // TODO: @David Add additional results
}

@Injectable()
export class WorkflowService {

  constructor(private http: HttpClient, private bar: MatSnackBar) { }

  private getKeyFromId(id: number): Observable<string> {
    return this.http.get<{ [key: string]: Workflow }>(`https://wpsflow.firebaseio.com/workflow.json`).pipe(
      map(obj => Object.entries(obj).find(([key, workflow]) => workflow.id === id)),
      map(([key, workflow]) => key)
    );
  }

  public all(): Observable<Workflow[]> {
    return this.http.get<{ [key: string]: Workflow }>(`https://wpsflow.firebaseio.com/workflow.json`).pipe(
      map(obj => Object.values(obj))
    );
  }

  public get(id: number): Observable<Workflow> {
    return this.getKeyFromId(id).pipe(
      switchMap(key => this.http.get<Workflow>(`https://wpsflow.firebaseio.com/workflow/${key}.json`))
    );
  }

  public create(workflow: Partial<Workflow>): Observable<Workflow> {
    this.bar.open(`Created Workflow`, 'CLOSE', { duration: 3000 });
    return this.http.post<Workflow>(`https://wpsflow.firebaseio.com/workflow.json`, workflow).pipe(
      map(obj => <Workflow>workflow)
    );
  }

  public update(id: number, workflow: Partial<Workflow>): Observable<Workflow> {
    this.bar.open(`Saved Workflow`, 'CLOSE', { duration: 3000 });
    return this.getKeyFromId(id).pipe(
      switchMap(key => this.http.put<Workflow>(`https://wpsflow.firebaseio.com/workflow/${key}.json`, workflow))
    );
  }

  public async remove(id: number): Promise<boolean> {
    this.bar.open(`Deleted Workflow`, 'CLOSE', { duration: 3000 });
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
  public validate(workflow: Partial<Workflow>): WorkflowValidationResult {
    if (!workflow) {
      return WorkflowValidationResult.ERROR;
    }

    // check name
    if (workflow.title.length > 255) {
      return WorkflowValidationResult.TITLE_TO_LONG;
    } else if (workflow.title.length < 1) {
      return WorkflowValidationResult.TITLE_TO_SHORT;
    } else if (workflow.tasks && workflow.tasks.length < 1) {
      return WorkflowValidationResult.EMPTY;
    } else {

      if (workflow.edges) {
        for (let i = 0; i < workflow.edges.length; i++) {
          if (workflow.edges[i].a_id === workflow.edges[i].b_id) {
            return WorkflowValidationResult.LOOP_TO_SAME_TASK;
          }
          if (workflow.edges[i].input_id + 1 !== workflow.edges[i].output_id) {
            return WorkflowValidationResult.WRONG_INPUT_TYPES;
          }
        }
      }

    }

    // TODO: @David add additional checks
    // - cycle check

    return WorkflowValidationResult.SUCCESSFUL;
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
