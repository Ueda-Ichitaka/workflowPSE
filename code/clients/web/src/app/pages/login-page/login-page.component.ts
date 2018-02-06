import { Component, OnInit, ViewChild, ElementRef } from '@angular/core';
import { Observable } from 'rxjs/Observable';
import { ProcessService } from 'app/services/process.service';
import { WpsService } from 'app/services/wps.service';
import { WPS } from '../../models/WPS';
import { trigger, transition, style, animate } from '@angular/animations';


@Component({
  selector: 'app-login-page',
  templateUrl: './login-page.component.html',
  styleUrls: ['./login-page.component.scss'],
})
export class LoginPageComponent implements OnInit {



  constructor(
    private processService: ProcessService,
    private wpsService: WpsService,
  ) {

  }

  public ngOnInit(): void {

  }

}
