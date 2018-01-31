import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { Process } from '../models/Process';
import { ProcessParameterType } from '../models/ProcessParameter';
import { map } from 'rxjs/operators';

@Injectable()
export class ProcessService {

  /**
   * return color for each process parameter type
   * @param {ProcessParameterType} type
   * @returns {string} Hexadecimal color number as string
   */
  public static getTypeColor(type: ProcessParameterType): string {
    switch (type) {
      case ProcessParameterType.LITERAL: return '#03A9F4';
      case ProcessParameterType.COMPLEX: return '#FFC107';
      case ProcessParameterType.BOUNDING_BOX: return '#4CAF50';
      default: return '#000000';
    }
  }

  /**
   * return the name of each process parameter type
   * @param {ProcessParameterType} type
   * @returns {string} name
   */
  public static getTypeName(type: ProcessParameterType): string {
    switch (type) {
      case ProcessParameterType.LITERAL: return 'Literal';
      case ProcessParameterType.COMPLEX: return 'Complex';
      case ProcessParameterType.BOUNDING_BOX: return 'Bounding Box';
      default: return 'Undefined';
    }
  }

  /**
   * Constructs process Service
   * @param {HttpClient} http
   */
  constructor(private http: HttpClient) { }

  /**
   * Returns observable of all processes
   * @returns {Observable<Process[]>}
   */
  public all(): Observable<Process[]> {
    return this.http.get<Process[]>(`http://127.0.0.1:8000/process/`);
  }

  /**
   * Returns process with given id
   * @param {number} id
   * @returns {Observable<Process>}
   */
  public get(id: number): Observable<Process> {
    return this.http.get<Process>(`http://127.0.0.1:8000/process/${id}`);
  }
}
