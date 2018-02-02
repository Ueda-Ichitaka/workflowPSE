import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { ArtefactDialogComponent } from './artefact-dialog.component';

describe('ProcessDetailDialogComponent', () => {
  let component: ArtefactDialogComponent;
  let fixture: ComponentFixture<ArtefactDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ArtefactDialogComponent]
    })
      .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(ArtefactDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
