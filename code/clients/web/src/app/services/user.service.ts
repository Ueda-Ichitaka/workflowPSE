import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { map } from 'rxjs/operators';
import { User } from 'app/models/User';
import { Router } from '@angular/router';
import { catchError } from 'rxjs/operators/catchError';
import { ErrorObservable } from 'rxjs/observable/ErrorObservable';

@Injectable()
export class UserService {
    constructor(private http: HttpClient, private router: Router) { }

    public get(): Observable<User> {
        return this.http.get<User>('http://127.0.0.1:8000/user/', { withCredentials: true }).pipe(
            catchError(error => {
                this.router.navigate(['/login']);
                return new ErrorObservable(error);
            })
        );
    }

    public login(username: string, password: string): Observable<User> {
        return this.http.post<User>('http://127.0.0.1:8000/login/', { username, password }, { withCredentials: true });
    }

    public async logout(): Promise<any> {
        return this.http.delete<any>('http://127.0.0.1:8000/logout/').toPromise();
    }

}
