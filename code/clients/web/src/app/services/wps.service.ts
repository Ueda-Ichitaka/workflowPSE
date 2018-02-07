import { Injectable } from '@angular/core';
import { WPS } from '../models/WPS';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { map, switchMap, catchError } from 'rxjs/operators';
import { ErrorObservable } from 'rxjs/observable/ErrorObservable';
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
    return this.http.get<WPS[]>(`http://127.0.0.1:8000/wps/`, { withCredentials: true });
  }


  /**
   * Create WPS and returns observable of WPS
   * currently disabled
   * @param {string} url
   * @returns {Observable<WPS>}
   */
  public create(url: string): Observable<WPS> {
    this.bar.open(`Created WPS`, 'CLOSE', { duration: 3000 });
    return this.http.post<WPS>(`http://127.0.0.1:8000/wps/`, url, { withCredentials: true }).pipe(
      catchError((error) => {
        this.bar.open(`ERROR. Can not add WPS Server. Wrong URL?`, 'CLOSE', { duration: 5000 });
        return new ErrorObservable(`can't create wps`);
      })
    );
  }

  /**
   * Removes WPS with given id
   * @param {number} id
   * @returns {Promise<boolean>}
   */
  public async remove(id: number): Promise<boolean> {
    this.bar.open(`Deleted WPS`, 'CLOSE', { duration: 3000 });
    return this.http.delete<boolean>(`http://127.0.0.1:8000/wps/${id}`, { withCredentials: true }).toPromise();
  }

  public async refresh(): Promise<boolean> {
    this.bar.open(`Refreshed WPS Processes`, 'CLOSE', { duration: 3000 });
    const result = this.http.get<boolean>(`http://127.0.0.1:8000/wps_refresh/`, { withCredentials: true }).toPromise();
    return result['error'] === undefined;
  }
}
