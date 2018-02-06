import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs/Observable';
import { map } from 'rxjs/operators';
import { User } from 'app/models/User';

@Injectable()
export class UserService {
    constructor(private http: HttpClient) { }

    public get(): Observable<User> {
        return this.http.get<User>('http://127.0.0.1:8000/user/');
    }

    public login(name: string, password: string): Promise<User> {

    }
}
