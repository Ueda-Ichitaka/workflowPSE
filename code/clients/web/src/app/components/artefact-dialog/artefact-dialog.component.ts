import { Component, OnInit, Inject, ViewEncapsulation, ViewChild, ElementRef } from '@angular/core';
import { MAT_DIALOG_DATA } from '@angular/material';
import { Artefact } from 'app/models/Artefact';
import { ProcessParameter } from 'app/models/ProcessParameter';
import { ProcessService } from 'app/services/process.service';

declare var hljs: any;
@Component({
  selector: 'app-artefact-dialog',
  templateUrl: './artefact-dialog.component.html',
  styleUrls: ['./artefact-dialog.component.scss'],
})
export class ArtefactDialogComponent implements OnInit {

  public selectedFormat = 'markdown';
  public data;

  public editMode = true;

  constructor( @Inject(MAT_DIALOG_DATA) public parameter: ProcessParameter<'input' | 'output'>) {

  }

  @ViewChild('code')
  public codeComponent: ElementRef;

  @ViewChild('text')
  public textAreaComponent: ElementRef;

  public ngOnInit() {
  }

  public getTypeInfo(type: number): [string, string] {
    return [ProcessService.getTypeName(type), ProcessService.getTypeColor(type)];
  }


  public clickEditButton() {
    if (this.editMode) {
      const el: HTMLElement = this.codeComponent.nativeElement;
      el.className = '';
      el.classList.add(this.selectedFormat);
      el.innerHTML = '';

      el.appendChild(document.createTextNode(this.data));

      setTimeout(() => {
        hljs.highlightBlock(el);
      }, 20);
    }

    this.editMode = !this.editMode;
  }
}
