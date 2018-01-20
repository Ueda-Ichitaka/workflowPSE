import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { Process } from '../models/Process';
import { ProcessParameterType } from '../models/ProcessParameter';
import { catchError, map, tap, switchMap } from 'rxjs/operators';
import { of } from 'rxjs/observable/of';
import { Subscriber } from 'rxjs/Subscriber';

@Injectable()
export class ProcessService {

  public static getTypeColor(type: ProcessParameterType): string {
    switch (type) {
      case ProcessParameterType.LITERAL: return '#03A9F4';
      case ProcessParameterType.COMPLEX: return '#FFC107';
      case ProcessParameterType.BOUNDING_BOX: return '#4CAF50';
      default: return '#000000';
    }
  }

  public static getTypeName(type: ProcessParameterType): string {
    switch (type) {
      case ProcessParameterType.LITERAL: return 'Literal';
      case ProcessParameterType.COMPLEX: return 'Complex';
      case ProcessParameterType.BOUNDING_BOX: return 'Bounding Box';
      default: return 'Undefined';
    }
  }

  constructor(private http: HttpClient) { }

  public all(): Observable<Process[]> {
    return this.http.get<Process[]>(`https://wpsflow.firebaseio.com/process.json`);
  }

  public get(id: number): Observable<Process> {
    return this.http.get<Process>(`https://wpsflow.firebaseio.com/process/${id}.json`);
  }

  public create(process: Partial<Process>): Observable<Process> {
    return this.http.post<Process>(`https://wpsflow.firebaseio.com/process.json`, process);
  }

  public update(id: number, process: Partial<Process>): Observable<Process> {
    return this.http.post<Process>(`https://wpsflow.firebaseio.com/process/${id}.json`, process);
  }

  public async remove(id: number): Promise<boolean> {
    return this.http.delete<boolean>(`https://wpsflow.firebaseio.com/process/${id}.json`).toPromise();
  }
}
