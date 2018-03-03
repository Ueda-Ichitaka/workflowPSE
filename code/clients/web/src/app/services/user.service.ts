import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { map } from 'rxjs/operators';
import { User } from 'app/models/User';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators/catchError';
import { ErrorObservable } from 'rxjs/observable/ErrorObservable';
import { environment } from 'environments/environment';

@Injectable()
export class UserService {
    constructor(private http: HttpClient, private router: Router) { }

    public get(): Observable<User> {
        return this.http.get<User>(`${environment.ip}/user/`, { withCredentials: true }).pipe(
            catchError(error => {
                this.router.navigate(['/login']);
                return new ErrorObservable(error);
            })
        );
    }

    public login(username: string, password: string): Observable<User> {
        return this.http.post<User>(`${environment.ip}/login/`, { username, password }, { withCredentials: true });
    }

    public async logout(): Promise<any> {
        return this.http.delete<any>(`${environment.ip}/logout/`).toPromise();
    }

}
