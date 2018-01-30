import { Injectable } from '@angular/core';
import { WPS } from '../models/WPS';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { map, switchMap } from 'rxjs/operators';
import { MatSnackBar } from '@angular/material';

@Injectable()
export class WpsService {
  /**
   * Constructs wps service
   * @param {HttpClient} http
   * @param {MatSnackBar} bar
   */
  constructor(private http: HttpClient, private bar: MatSnackBar) { }


  /**
   * Returns an observable to all WPS
   * @returns {Observable<WPS[]>}
   */
  public all(): Observable<WPS[]> {
    return this.http.get<WPS[]>(`http://127.0.0.1:8000/wps/`);
  }


  /**
   * Create WPS and returns observable of WPS
   * currently disabled
   * @param {string} url
   * @returns {Observable<WPS>}
   */
  public create(url: string): Observable<WPS> {
    this.bar.open(`Created WPS`, 'CLOSE', { duration: 3000 });
    return this.http.post<WPS>(`http://127.0.0.1:8000/wps/`, url);
  }

  /**
   * Removes WPS with given id
   * @param {number} id
   * @returns {Promise<boolean>}
   */
  public async remove(id: number): Promise<boolean> {
    this.bar.open(`Deleted WPS`, 'CLOSE', { duration: 3000 });
    return this.http.delete<boolean>(`http://127.0.0.1:8000/wps/${id}`).toPromise();
  }
}
