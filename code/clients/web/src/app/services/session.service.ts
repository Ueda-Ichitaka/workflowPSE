import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { Session } from '../models/Session'

@Injectable()
export class SessionService {

  /**
   * Constructs session Service
   * @param {HttpClient} http
   */
  constructor(private http: HttpClient) { }

  /**
   * Returns Observable of the Session with the given id
   * @param {number} id of the user
   * @returns {Observable<Session>} the users session
   */
  public get(id: number): Observable<Session> {
    return this.http.get<Session>(`http://127.0.0.1:8000/session/${id}`);
  }

  /**
   * Create an Observable to a given partial session
   * @param {Partial<Session>} session that is created
   * @returns {Observable<Session>} the created session
   */
  public create(workflow: Partial<Session>): Observable<Session> {
    return this.http.post<Session>(`http://127.0.0.1:8000/session/`, workflow);
  }

  /**
   * Refreshes the observable of the given session
   * @param {number} id of the user
   * @param {Partial<Session>} session which is to be updated
   * @returns {Observable<Session>} updated session
   */
  public update(id: number, workflow: Partial<Session>): Observable<Session> {
    return this.http.patch<Session>(`http://127.0.0.1:8000/session/${id}`, workflow);
  }

  /**
   * Removes the session with the given id
   * @param {number} id of the user
   * @returns {Promise<boolean>} if session has been removed
   */
  // TODO maybe don't use, django says its better to set is_active flag false instead of deleting
  // also client does not have to save sessions
  //public async remove(id: number): Promise<boolean> {
  //  return this.http.delete<boolean>(`http://127.0.0.1:8000/session/${id}`).toPromise();
  //}
}

